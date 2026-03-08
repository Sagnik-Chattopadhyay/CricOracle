from db import SessionLocal
from models import Team
from sqlalchemy import or_

def diagnostic():
    db = SessionLocal()
    name = "India"
    fmt = "T20I" # Or "T20 International" as sent by frontend
    
    print(f"Searching for: '{name}' | Format: '{fmt}'")
    
    # Priority 1: Exact Match
    team = db.query(Team).filter(Team.name == name).first()
    print(f"P1 Exact Match: {team.name if team else 'NONE'}")
    
    # Priority 2: Fuzzy match with Team Type filter
    ttype = 'Franchise' if fmt == 'IPL' else 'International'
    print(f"Filter Type: {ttype}")
    team_fuzzy = db.query(Team).filter(Team.name.ilike(f"%{name}%"), Team.team_type == ttype).first()
    print(f"P2 Fuzzy + Type: {team_fuzzy.name if team_fuzzy else 'NONE'}")
    
    # Check all matches for "India"
    all_matches = db.query(Team).filter(Team.name.ilike(f"%{name}%")).all()
    print(f"All matches for '%{name}%':")
    for t in all_matches:
        print(f" - {t.name} (Type: {t.team_type}, ID: {t.team_id})")
        
    db.close()

if __name__ == "__main__":
    diagnostic()
