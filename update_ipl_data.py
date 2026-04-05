"""
update_ipl_data.py — Full pipeline to refresh IPL data from Cricsheet.

Steps:
  1. Re-downloads the latest IPL CSV2 zip from cricsheet.org
  2. Ingests new match metadata (skips existing match_ids)
  3. Ingests deliveries for new matches only
  4. Runs enrichment (team types, venue countries)
  5. Prints a summary of what was added

Usage:
  python update_ipl_data.py            # Update IPL data only
  python update_ipl_data.py --all      # Update all formats (IPL, T20I, ODI, Tests)
"""

import os
import sys
import shutil
import requests
import zipfile
import io
import datetime
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import SessionLocal, engine, get_canonical_team_name
from models import Base, Team, Venue, Match, Player, Delivery

# ---- Configuration ----
DATA_DIR = "data"
CRICSHEET_URLS = {
    "IPL": "https://cricsheet.org/downloads/ipl_male_csv2.zip",
    "T20I": "https://cricsheet.org/downloads/t20s_male_csv2.zip",
    "ODI": "https://cricsheet.org/downloads/odis_male_csv2.zip",
    "Tests": "https://cricsheet.org/downloads/tests_male_csv2.zip",
}


def download_format(fmt: str, force: bool = True):
    """Download and extract Cricsheet CSV2 data for a format."""
    url = CRICSHEET_URLS.get(fmt)
    if not url:
        print(f"  [SKIP] Unknown format: {fmt}")
        return False

    fmt_dir = os.path.join(DATA_DIR, fmt)

    if force and os.path.exists(fmt_dir):
        print(f"  [CLEAN] Removing old {fmt} data directory...")
        shutil.rmtree(fmt_dir)

    os.makedirs(fmt_dir, exist_ok=True)

    print(f"  [DOWNLOAD] {url}")
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(fmt_dir)
        file_count = len(os.listdir(fmt_dir))
        print(f"  [OK] Extracted {file_count} files to {fmt_dir}")
        return True
    except Exception as e:
        print(f"  [ERROR] Download failed: {e}")
        return False


def get_or_create(session, model, lookup_kwargs, create_kwargs=None):
    """Get existing or create new record."""
    instance = session.query(model).filter_by(**lookup_kwargs).first()
    if instance:
        return instance
    if create_kwargs is None:
        create_kwargs = lookup_kwargs
    else:
        create_kwargs.update(lookup_kwargs)
    instance = model(**create_kwargs)
    session.add(instance)
    session.flush()
    return instance


def ingest_match_info(file_path, format_name, db: Session):
    """Ingest a single match info CSV. Returns True if new match was added."""
    try:
        info = {}
        teams_list = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(',')
                if not parts or parts[0] != 'info' or len(parts) < 3:
                    continue
                key = parts[1]
                val = parts[2].strip('"')
                if key == 'team':
                    teams_list.append(val)
                else:
                    info[key] = val

        if not teams_list:
            return False

        # Extract match_id from filename
        match_id_str = os.path.basename(file_path).split('_')[0]
        match_id = int(match_id_str)

        # Skip if match already exists
        existing = db.query(Match).filter_by(match_id=match_id).first()
        if existing:
            return False

        # Get or create Teams
        team_objs = []
        for t_name in teams_list:
            canonical_name = get_canonical_team_name(t_name)
            team_objs.append(get_or_create(db, Team, {'name': canonical_name}))

        # Ingest Players from registry
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 5 and parts[1] == 'registry' and parts[2] == 'people':
                    p_name = parts[3].strip('"')
                    p_id = parts[4].strip('"')
                    get_or_create(db, Player, {'cricsheet_id': p_id}, {'name': p_name})

        # Get or create Venue
        venue_name = info.get('venue', 'Unknown')
        city = info.get('city', 'Unknown')
        venue_obj = get_or_create(db, Venue, {'name': venue_name}, {'city': city})

        # Parse Date
        date_str = info.get('date', '')
        try:
            match_date = datetime.datetime.strptime(date_str, '%Y/%m/%d').date()
        except:
            match_date = datetime.date.today()

        toss_winner_name = info.get('toss_winner')
        toss_winner_id = None
        if toss_winner_name:
            t_obj = db.query(Team).filter_by(name=toss_winner_name).first()
            if t_obj:
                toss_winner_id = t_obj.team_id

        winner_name = info.get('winner')
        winner_id = None
        if winner_name:
            t_obj = db.query(Team).filter_by(name=winner_name).first()
            if t_obj:
                winner_id = t_obj.team_id

        new_match = Match(
            match_id=match_id,
            team_a_id=team_objs[0].team_id if len(team_objs) > 0 else None,
            team_b_id=team_objs[1].team_id if len(team_objs) > 1 else None,
            venue_id=venue_obj.venue_id,
            date=match_date,
            format=format_name,
            toss_winner_id=toss_winner_id,
            toss_decision=info.get('toss_decision'),
            winner_id=winner_id,
            win_margin=str(info.get('winner_runs', info.get('winner_wickets', '')))
        )
        db.add(new_match)
        return True

    except Exception as e:
        print(f"    [WARN] Error ingesting {os.path.basename(file_path)}: {e}")
        return False


def ingest_deliveries_for_match(file_path, db: Session, team_cache, player_cache):
    """Ingest deliveries for a single match CSV."""
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return False

        match_id = int(df['match_id'].iloc[0])

        # Check if deliveries already exist for this match
        existing_count = db.query(func.count(Delivery.delivery_id)).filter_by(match_id=match_id).scalar()
        if existing_count > 0:
            return False

        deliveries = []
        for _, row in df.iterrows():
            innings = int(row['innings'])
            ball_val = float(row['ball'])
            over_num = int(ball_val)
            ball_num = int(round((ball_val - over_num) * 10))

            batting_team_id = team_cache.get(get_canonical_team_name(row['batting_team']))
            bowling_team_id = team_cache.get(get_canonical_team_name(row['bowling_team']))

            striker_id = player_cache.get(row['striker'])
            non_striker_id = player_cache.get(row['non_striker'])
            bowler_id = player_cache.get(row['bowler'])

            player_dismissed_name = row.get('player_dismissed')
            player_dismissed_id = player_cache.get(player_dismissed_name) if pd.notna(player_dismissed_name) else None

            delivery = Delivery(
                match_id=match_id,
                innings=innings,
                over=over_num,
                ball=ball_num,
                batting_team_id=batting_team_id,
                bowling_team_id=bowling_team_id,
                batsman_id=striker_id,
                non_striker_id=non_striker_id,
                bowler_id=bowler_id,
                runs_off_bat=int(row['runs_off_bat']),
                extras=int(row['extras']),
                wicket_type=row['wicket_type'] if pd.notna(row.get('wicket_type')) else None,
                player_dismissed_id=player_dismissed_id
            )
            deliveries.append(delivery)

        db.bulk_save_objects(deliveries)
        return True

    except Exception as e:
        print(f"    [WARN] Error in deliveries {os.path.basename(file_path)}: {e}")
        return False


def enrich_data(db: Session):
    """Enrich team types and venue countries."""
    print("\n[STEP 4] Enriching data...")

    # Team types
    from sqlalchemy import or_
    ipl_teams_query = db.query(Team.team_id).join(
        Match, (Match.team_a_id == Team.team_id) | (Match.team_b_id == Team.team_id)
    ).filter(Match.format == 'IPL').distinct()
    ipl_team_ids = [r[0] for r in ipl_teams_query.all()]

    db.query(Team).filter(Team.team_id.in_(ipl_team_ids)).update(
        {Team.team_type: 'Franchise'}, synchronize_session=False
    )
    db.query(Team).filter(~Team.team_id.in_(ipl_team_ids)).update(
        {Team.team_type: 'International'}, synchronize_session=False
    )
    print(f"  [OK] Tagged {len(ipl_team_ids)} franchise teams")

    # Venue countries
    venue_country_map = {
        'India': ['Mumbai', 'Bangalore', 'Bengaluru', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata',
                  'Ahmedabad', 'Pune', 'Jaipur', 'Mohali', 'Dharamsala', 'Indore', 'Lucknow',
                  'Guwahati', 'Visakhapatnam', 'Cuttack', 'Nagpur', 'Ranchi', 'Rajkot', 'Kanpur',
                  'Navi Mumbai', 'Thiruvananthapuram', 'Raipur'],
        'United Arab Emirates': ['Dubai', 'Abu Dhabi', 'Sharjah'],
        'South Africa': ['Cape Town', 'Johannesburg', 'Durban', 'Centurion', 'Port Elizabeth',
                         'Bloemfontein', 'East London', 'Paarl', 'Potchefstroom'],
        'England': ['London', 'Birmingham', 'Manchester', 'Nottingham', 'Leeds', 'Southampton',
                    'Cardiff', 'Bristol', 'Chester-le-Street'],
        'Australia': ['Melbourne', 'Sydney', 'Brisbane', 'Perth', 'Adelaide', 'Hobart', 'Canberra',
                      'Gold Coast', 'Geelong'],
        'New Zealand': ['Auckland', 'Wellington', 'Christchurch', 'Hamilton', 'Dunedin',
                        'Mount Maunganui', 'Napier', 'Nelson'],
        'West Indies': ['St Kitts', 'Barbados', 'Guyana', 'Trinidad', 'Antigua', 'Jamaica',
                        'St Lucia', 'Grenada', 'Basseterre', 'Bridgetown'],
        'Sri Lanka': ['Colombo', 'Kandy', 'Galle', 'Hambantota', 'Dambulla', 'Pallekele'],
        'Pakistan': ['Lahore', 'Karachi', 'Rawalpindi', 'Multan', 'Faisalabad'],
        'Bangladesh': ['Dhaka', 'Chittagong', 'Sylhet', 'Mirpur'],
        'Zimbabwe': ['Harare', 'Bulawayo'],
    }

    venues = db.query(Venue).all()
    venue_update_count = 0
    for v in venues:
        assigned = False
        for country, cities in venue_country_map.items():
            if v.city and any(city.lower() in v.city.lower() for city in cities):
                v.country = country
                assigned = True
                break
            if any(city.lower() in v.name.lower() for city in cities):
                v.country = country
                assigned = True
                break
        if not assigned:
            v.country = "India"  # Default for IPL venues
        venue_update_count += 1

    print(f"  [OK] Updated {venue_update_count} venue countries")
    db.commit()


def run_update(formats_to_update=None):
    """Main update pipeline."""
    if formats_to_update is None:
        formats_to_update = ["IPL"]

    print("=" * 60)
    print("  CricPredict Data Update Pipeline")
    print(f"  Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Formats: {', '.join(formats_to_update)}")
    print("=" * 60)

    # Ensure DB tables exist
    Base.metadata.create_all(engine)
    db = SessionLocal()

    # Pre-update stats
    for fmt in formats_to_update:
        count_before = db.query(func.count(Match.match_id)).filter(Match.format == fmt).scalar()
        latest = db.query(func.max(Match.date)).filter(Match.format == fmt).scalar()
        print(f"\n  [BEFORE] {fmt}: {count_before} matches, latest: {latest}")

    # Step 1: Download
    print(f"\n[STEP 1] Downloading latest Cricsheet data...")
    for fmt in formats_to_update:
        print(f"\n  --- {fmt} ---")
        download_format(fmt, force=True)

    # Step 2: Ingest match info
    print(f"\n[STEP 2] Ingesting match metadata...")
    total_new_matches = 0
    for fmt in formats_to_update:
        fmt_path = os.path.join(DATA_DIR, fmt)
        if not os.path.exists(fmt_path):
            continue

        info_files = [f for f in os.listdir(fmt_path) if f.endswith("_info.csv")]
        new_count = 0
        for i, f in enumerate(info_files):
            if ingest_match_info(os.path.join(fmt_path, f), fmt, db):
                new_count += 1
            if (i + 1) % 200 == 0:
                db.commit()  # Periodic commit
                print(f"    Processed {i + 1}/{len(info_files)} files...")

        db.commit()
        total_new_matches += new_count
        print(f"  [OK] {fmt}: {new_count} new matches ingested (out of {len(info_files)} files)")

    # Step 3: Ingest deliveries for new matches
    print(f"\n[STEP 3] Ingesting deliveries for new matches...")

    # Rebuild caches after match info ingestion
    teams = db.query(Team).all()
    team_cache = {t.name: t.team_id for t in teams}
    all_players = db.query(Player).all()
    player_cache = {p.name: p.player_id for p in all_players}
    print(f"  Caches: {len(team_cache)} teams, {len(player_cache)} players")

    total_new_deliveries = 0
    for fmt in formats_to_update:
        fmt_path = os.path.join(DATA_DIR, fmt)
        if not os.path.exists(fmt_path):
            continue

        csv_files = [f for f in os.listdir(fmt_path) if f.endswith(".csv") and not f.endswith("_info.csv")]
        new_del_count = 0
        for i, f in enumerate(csv_files):
            if ingest_deliveries_for_match(os.path.join(fmt_path, f), db, team_cache, player_cache):
                new_del_count += 1
            if (i + 1) % 100 == 0:
                db.commit()
                print(f"    Processed {i + 1}/{len(csv_files)} delivery files...")

        db.commit()
        total_new_deliveries += new_del_count
        print(f"  [OK] {fmt}: Deliveries ingested for {new_del_count} new matches")

    # Step 4: Enrichment
    enrich_data(db)

    # Post-update stats
    print("\n" + "=" * 60)
    print("  UPDATE SUMMARY")
    print("=" * 60)
    for fmt in formats_to_update:
        count_after = db.query(func.count(Match.match_id)).filter(Match.format == fmt).scalar()
        latest = db.query(func.max(Match.date)).filter(Match.format == fmt).scalar()
        print(f"  {fmt}: {count_after} total matches, latest: {latest}")

    # IPL 2026 specific check
    from datetime import date
    ipl_2026 = db.query(func.count(Match.match_id)).filter(
        Match.format == 'IPL', Match.date >= date(2026, 1, 1)
    ).scalar()
    print(f"\n  IPL 2026 matches: {ipl_2026}")
    print(f"  New matches added: {total_new_matches}")
    print(f"  New delivery sets added: {total_new_deliveries}")
    print("=" * 60)

    db.close()


if __name__ == "__main__":
    if "--all" in sys.argv:
        run_update(["IPL", "T20I", "ODI", "Tests"])
    else:
        run_update(["IPL"])
