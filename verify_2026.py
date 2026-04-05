from db import SessionLocal
from models import Player, Team
from sqlalchemy import text

db = SessionLocal()

print("=== VERIFYING 2026 SQUAD REFRESH ===")

# 1. Check CSK
csk = db.query(Team).filter(Team.name.like('%Chennai%')).first()
if csk:
    print(f"Team: {csk.name} (ID: {csk.team_id})")
    players = db.query(Player).filter(Player.franchise_team_id == csk.team_id).all()
    print(f"CSK Squad size: {len(players)}")
    for p in players[:5]: # Show top 5
        print(f"  - {p.name} ({p.role})")
    
    # Check Sanju Samson specifically
    sanju = db.query(Player).filter(Player.name == 'Sanju Samson').first()
    if sanju:
        print(f"Sanju Samson Roster: Franchise ID={sanju.franchise_team_id}")
        if sanju.franchise_team_id == csk.team_id:
            print("  ✅ Sanju Samson is in CSK 2026!")
        else:
            print(f"  ❌ Sanju Samson is in team {sanju.franchise_team_id}")

# 2. Check RCB
rcb = db.query(Team).filter(Team.name.like('%Royal Challengers%')).first()
if rcb:
    print(f"\nTeam: {rcb.name} (ID: {rcb.team_id})")
    players = db.query(Player).filter(Player.franchise_team_id == rcb.team_id).all()
    print(f"RCB Squad size: {len(players)}")
    for p in players[:5]:
        print(f"  - {p.name} ({p.role})")
    
    phil_salt = db.query(Player).filter(Player.name == 'Phil Salt').first()
    if phil_salt:
        if phil_salt.franchise_team_id == rcb.team_id:
             print("  ✅ Phil Salt is in RCB 2026!")

# 3. Check Left Players
print("\nVerifying 'Released' Players:")
left_players = ["Mayank Agarwal", "Devon Conway"]
for name in left_players:
    player = db.query(Player).filter(Player.name.like(f"%{name}%")).first()
    if player:
        print(f"  {player.name}: Franchise={player.franchise_team_id}, International={player.intl_team_id}")
        if player.franchise_team_id is None:
            print(f"  ✅ {player.name} correctly has no franchise mapping for 2026.")
        else:
            print(f"  ❌ {player.name} still mapped to team {player.franchise_team_id}")

# 4. Check India
india = db.query(Team).filter(Team.name == 'India').first()
if india:
    print(f"\nTeam: {india.name} (ID: {india.team_id})")
    players = db.query(Player).filter(Player.intl_team_id == india.team_id).all()
    print(f"India Squad size: {len(players)}")

db.close()
