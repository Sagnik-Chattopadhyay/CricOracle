import pandas as pd
import os
import datetime
from sqlalchemy.orm import Session
from db import SessionLocal, engine, get_canonical_team_name
from models import Base, Team, Venue, Match, Player

def get_or_create(session, model, lookup_kwargs, create_kwargs=None):
    instance = session.query(model).filter_by(**lookup_kwargs).first()
    if instance:
        return instance
    else:
        if create_kwargs is None:
            create_kwargs = lookup_kwargs
        else:
            # Merge lookup into create
            create_kwargs.update(lookup_kwargs)
            
        instance = model(**create_kwargs)
        session.add(instance)
        # Flush to get the ID but don't commit yet
        session.flush()
        return instance

def ingest_match_info(file_path, league, format_name, db: Session):
    try:
        info = {}
        teams_list = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(',')
                if not parts or parts[0] != 'info' or len(parts) < 3:
                    continue
                
                key = parts[1]
                # Value might be quoted or contain commas (though split(',') handles basic cases)
                # For more robustness, I'll use the csv module later if needed, but let's try this.
                val = parts[2].strip('"')
                
                if key == 'team':
                    teams_list.append(val)
                else:
                    info[key] = val
        
        if not teams_list: return False
        
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
                    # Only lookup by cricsheet_id
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
            if t_obj: toss_winner_id = t_obj.team_id

        winner_name = info.get('winner')
        winner_id = None
        if winner_name:
            t_obj = db.query(Team).filter_by(name=winner_name).first()
            if t_obj: winner_id = t_obj.team_id

        match_id_str = os.path.basename(file_path).split('_')[0]
        match_id = int(match_id_str)
        
        existing_match = db.query(Match).filter_by(match_id=match_id).first()
        if not existing_match:
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
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error ingesting {file_path}: {str(e)}")
        return False

def run_ingestion():
    # Initialize Database
    print("Initialising database tables...")
    Base.metadata.create_all(engine)
    
    db = SessionLocal()
    data_dir = "data"
    formats = ["IPL", "T20I", "ODI", "Tests"]
    
    for fmt in formats:
        fmt_path = os.path.join(data_dir, fmt)
        if not os.path.exists(fmt_path): continue
        
        print(f"Ingesting metadata for {fmt}...")
        info_files = [f for f in os.listdir(fmt_path) if f.endswith("_info.csv")]
        count = 0
        for f in info_files:
            if ingest_match_info(os.path.join(fmt_path, f), fmt, fmt, db):
                count += 1
            if count % 100 == 0:
                print(f"Processed {count} matches...")
        
        print(f"Finished {fmt}: Ingested {count} matches.")
    
    db.close()

if __name__ == "__main__":
    run_ingestion()
