import pandas as pd
import os
from sqlalchemy.orm import Session
from db import SessionLocal, engine
from models import Delivery, Match, Team, Player
import tqdm

def get_player_map(db: Session, match_id):
    # This might be slow if called per match, but let's see.
    # Actually, cricsheet match csv uses player names, but info.csv has names too.
    # I should build a cache of names to IDs.
    pass

def ingest_match_deliveries(file_path, db: Session, team_cache, player_cache):
    try:
        df = pd.read_csv(file_path)
        deliveries = []
        
        match_id = int(df['match_id'].iloc[0])
        
        for index, row in df.iterrows():
            innings = int(row['innings'])
            # ball 0.1 -> over 0, ball 1
            ball_val = float(row['ball'])
            over_num = int(ball_val)
            ball_num = int(round((ball_val - over_num) * 10))
            
            # Look up teams and players from cache or DB
            batting_team_name = row['batting_team']
            bowling_team_name = row['bowling_team']
            
            batting_team_id = team_cache.get(batting_team_name)
            bowling_team_id = team_cache.get(bowling_team_name)
            
            striker_name = row['striker']
            non_striker_name = row['non_striker']
            bowler_name = row['bowler']
            
            # NOTE: Player names in delivery CSV might not be unique if only using name.
            # But the info.csv had name-to-ID mapping.
            # I'll look up by name in the player_cache which should be built from info.csv for this match.
            striker_id = player_cache.get(striker_name)
            non_striker_id = player_cache.get(non_striker_name)
            bowler_id = player_cache.get(bowler_name)
            
            player_dismissed_name = row['player_dismissed']
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
                wicket_type=row['wicket_type'] if pd.notna(row['wicket_type']) else None,
                player_dismissed_id=player_dismissed_id
            )
            deliveries.append(delivery)
            
        db.bulk_save_objects(deliveries)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        # print(f"Error in {file_path}: {e}")
        return False

def run_delivery_ingestion():
    db = SessionLocal()
    data_dir = "data"
    formats = ["IPL", "T20I", "ODI", "Tests"]
    
    # Pre-build team and player caches for performance
    print("Building caches...")
    teams = db.query(Team).all()
    team_cache = {t.name: t.team_id for t in teams}
    
    all_players = db.query(Player).all()
    player_cache = {p.name: p.player_id for p in all_players}
    print(f"Caches built: {len(team_cache)} teams, {len(player_cache)} players.")
    
    for fmt in formats:
        fmt_path = os.path.join(data_dir, fmt)
        if not os.path.exists(fmt_path): continue
        
        print(f"Ingesting deliveries for {fmt}...")
        csv_files = [f for f in os.listdir(fmt_path) if f.endswith(".csv") and not f.endswith("_info.csv")]
        
        for f in tqdm.tqdm(csv_files):
            ingest_match_deliveries(os.path.join(fmt_path, f), db, team_cache, player_cache)
            
    db.close()

if __name__ == "__main__":
    run_delivery_ingestion()
