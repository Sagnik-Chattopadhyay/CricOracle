import os
from datetime import datetime
from db import SessionLocal
from models import Match, Team, Venue, Delivery, Player
from api_connector import CricketDataAPI
from sqlalchemy.orm import Session

FORMAT_MAP = {
    "t20": "T20I",
    "madi": "ODI",
    "test": "Tests",
    "ipl": "IPL"
}

def get_or_create_team(db: Session, team_name):
    # Standardize names (e.g., "India" instead of "India Women" if we want to merge, but let's keep it exact for now)
    team = db.query(Team).filter(Team.name.ilike(team_name)).first()
    if not team:
        team = Team(name=team_name, team_type="International" if "Women" not in team_name else "International")
        db.add(team)
        db.flush()
    return team

def get_or_create_venue(db: Session, venue_name, city="Unknown"):
    venue = db.query(Venue).filter(Venue.name.ilike(f"%{venue_name}%")).first()
    if not venue:
        venue = Venue(name=venue_name, city=city)
        db.add(venue)
        db.flush()
    return venue

def get_or_create_player(db: Session, player_name, team_id=None):
    player = db.query(Player).filter(Player.name.ilike(player_name)).first()
    if not player:
        player = Player(name=player_name, team_id=team_id)
        db.add(player)
        db.flush()
    return player

def sync_recent_matches():
    db = SessionLocal()
    api = CricketDataAPI()
    
    print(f"[{datetime.now()}] Starting live sync...")
    
    response = api.get_current_matches()
    if not response or response.get("status") != "success":
        print("Failed to fetch matches from API.")
        return

    matches_data = response.get("data", [])
    synced_count = 0
    
    for m_data in matches_data:
        # Check if match is finished
        if m_data.get("matchEnded") != True:
            continue
            
        # CricAPI uses string IDs, we use int in DB
        # This is a mapping challenge: CricID vs CricsheetID vs OurID
        # For now, let's use a hashed or external mapping table if needed.
        # Simple check: Match date + Teams
        
        m_date_str = m_data.get("date") # "2026-03-08"
        try:
            m_date = datetime.strptime(m_date_str, "%Y-%m-%d").date()
        except:
            continue
            
        teams = m_data.get("teams", [])
        if len(teams) < 2: continue
        
        team_a_name = teams[0]
        team_b_name = teams[1]
        
        team_a = get_or_create_team(db, team_a_name)
        team_b = get_or_create_team(db, team_b_name)
        
        # Check if we already have this match today between these teams
        existing = db.query(Match).filter_by(
            date=m_date,
            team_a_id=team_a.team_id,
            team_b_id=team_b.team_id
        ).first()
        
        # Normalize Format
        m_type = m_data.get("matchType", "unknown")
        fmt = FORMAT_MAP.get(m_type, m_type.upper())
        
        match_obj = None
        if not existing:
            print(f"New match detected: {team_a_name} vs {team_b_name} ({m_date})")
            match_obj = Match(
                team_a_id=team_a.team_id,
                team_b_id=team_b.team_id,
                date=m_date,
                format=fmt,
                winner_id=get_or_create_team(db, m_data.get("status", "").split(" won")[0]).team_id if " won" in m_data.get("status", "") else None,
                win_margin=m_data.get("status", "")
            )
            db.add(match_obj)
            db.flush()
            synced_count += 1
        else:
            match_obj = existing
            if existing.format != fmt:
                existing.format = fmt
            if not existing.win_margin:
                existing.win_margin = m_data.get("status", "")

        # ENSURE DETAILED DATA (Scorecard, Venue, Performers)
        m_id = m_data.get("id")
        print(f"DEBUG: Checking scorecard for Match {m_id} ({team_a_name} vs {team_b_name})")
        scorecard_resp = api.get_match_scorecard(m_id)
        if scorecard_resp and scorecard_resp.get("status") == "success":
            sc_data = scorecard_resp.get("data", {})
            print(f"DEBUG: Success! Scorecard found for {m_id}. Venue: {sc_data.get('venue')}")
            
            # 1. Update Venue
            v_name = sc_data.get("venue", "Unknown")
            venue_obj = get_or_create_venue(db, v_name)
            match_obj.venue_id = venue_obj.venue_id
            
            # 2. Update Win Margin
            match_obj.win_margin = sc_data.get("status", match_obj.win_margin)
            
            # 3. Populate Deliveries (Summary records)
            db.query(Delivery).filter_by(match_id=match_obj.match_id).delete()
            
            # Find a placeholder player for wickets if needed
            placeholder_player = db.query(Player).first()
            placeholder_id = placeholder_player.player_id if placeholder_player else 1

            for i, inning in enumerate(sc_data.get("scorecard", [])):
                inning_name = inning.get("inning", "")
                batting_team_name_sc = inning_name.split(" Inning")[0]
                batting_team = get_or_create_team(db, batting_team_name_sc)
                bowling_team = team_b if batting_team.team_id == team_a.team_id else team_a
                
                # Top Batters
                for b_data in inning.get("batting", [])[:3]:
                    p_name = b_data.get("name")
                    player = get_or_create_player(db, p_name, batting_team.team_id)
                    db.add(Delivery(
                        match_id=match_obj.match_id, innings=i+1, over=0, ball=1,
                        batting_team_id=batting_team.team_id, bowling_team_id=bowling_team.team_id,
                        batsman_id=player.player_id, runs_off_bat=int(b_data.get("r", 0)), extras=0
                    ))
                
                # Top Bowlers (and Wickets)
                for bw_data in inning.get("bowling", [])[:3]:
                    p_name = bw_data.get("name")
                    player = get_or_create_player(db, p_name, bowling_team.team_id)
                    wkt_count = int(bw_data.get("w", 0))
                    for _ in range(wkt_count):
                        db.add(Delivery(
                            match_id=match_obj.match_id, innings=i+1, over=0, ball=1,
                            batting_team_id=batting_team.team_id, bowling_team_id=bowling_team.team_id,
                            bowler_id=player.player_id, runs_off_bat=0, extras=0,
                            player_dismissed_id=placeholder_id
                        ))
                
                # Balance Runs
                total_runs = 0
                for s_sum in m_data.get("score", []):
                    if batting_team_name_sc in s_sum.get("inning", ""):
                        total_runs = int(s_sum.get("r", 0))
                        break
                
                current_sum = sum(int(b.get("r", 0)) for b in inning.get("batting", []))
                if total_runs > current_sum:
                    db.add(Delivery(
                        match_id=match_obj.match_id, innings=i+1, 
                        over=int(inning.get("o", 0)) - 1 if inning.get("o", 0) > 0 else 0, ball=6,
                        batting_team_id=batting_team.team_id, bowling_team_id=bowling_team.team_id,
                        runs_off_bat=total_runs - current_sum, extras=0
                    ))
        else:
            print(f"DEBUG: Scorecard NOT found for {m_id}. Status: {scorecard_resp.get('status') if scorecard_resp else 'None'}")
            
    db.commit()
    print(f"Sync complete. Added {synced_count} new matches.")
    db.close()

if __name__ == "__main__":
    sync_recent_matches()
