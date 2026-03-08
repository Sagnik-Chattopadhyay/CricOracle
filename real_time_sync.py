import os
from datetime import datetime
from db import SessionLocal
from models import Match, Team, Venue, Delivery, Player
from api_connector import CricketDataAPI
from sqlalchemy.orm import Session

def get_or_create_team(db: Session, team_name):
    # Simple lookup for now, can be expanded
    team = db.query(Team).filter_by(name=team_name).first()
    if not team:
        team = Team(name=team_name)
        db.add(team)
        db.flush()
    return team

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
        
        if not existing:
            # New match found in API!
            print(f"New match detected: {team_a_name} vs {team_b_name} ({m_date})")
            
            # Create basic match record
            new_match = Match(
                team_a_id=team_a.team_id,
                team_b_id=team_b.team_id,
                date=m_date,
                format=m_data.get("matchType", "unknown"),
                winner_id=get_or_create_team(db, m_data.get("status", "").split(" won")[0]).team_id if " won" in m_data.get("status", "") else None
            )
            db.add(new_match)
            synced_count += 1
            
            # TODO: In a production version, we would call api.get_match_scorecard(m_data['id'])
            # and populate the 'deliveries' table here.
            # This requires complex JSON-to-Ball mapping logic.
            
    db.commit()
    print(f"Sync complete. Added {synced_count} new matches.")
    db.close()

if __name__ == "__main__":
    sync_recent_matches()
