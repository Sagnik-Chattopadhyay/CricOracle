from db import SessionLocal
from models import Team, Player
from sqlalchemy import or_

def check_data():
    db = SessionLocal()
    
    # 1. Check a few major teams and their player counts
    major_teams = ["Mumbai Indians", "Chennai Super Kings", "Royal Challengers Bangalore", "Kolkata Knight Riders"]
    print("--- SQUAD STATUS ---")
    for team_name in major_teams:
        team = db.query(Team).filter(Team.name.ilike(f"%{team_name}%")).first()
        if team:
            count = db.query(Player).filter_by(team_id=team.team_id).count()
            print(f"{team.name} (ID: {team.team_id}): {count} players")
        else:
            print(f"{team_name}: Team NOT FOUND in database")

    # 2. Check for players with NULL team_id or orphan team_ids
    print("\n--- ORPHAN CHECK ---")
    orphans = db.query(Player).filter(Player.team_id == None).count()
    print(f"Players with NULL team_id: {orphans}")
    
    # 3. Check player names for these teams to see if they exist at all
    print("\n--- SAMPLE PLAYER NAMES ---")
    mi_players = ["Rohit Sharma", "Hardik Pandya", "Jasprit Bumrah"]
    for p_name in mi_players:
        p = db.query(Player).filter(Player.name.ilike(f"%{p_name}%")).first()
        if p:
            print(f"Player {p.name} (ID: {p.player_id}): Assigned TeamID={p.team_id}")
        else:
            print(f"Player {p_name}: NOT FOUND in database")
            
    # 4. Identifying Team 25
    print("\n--- TEAM 25 INFO ---")
    t25 = db.query(Team).get(25)
    if t25:
        print(f"Team ID 25 is: {t25.name}")
        players_t25 = db.query(Player).filter_by(team_id=25).count()
        print(f"Team 25 player count: {players_t25}")
    else:
        print("Team ID 25 does not exist.")
        
    db.close()

if __name__ == "__main__":
    check_data()
