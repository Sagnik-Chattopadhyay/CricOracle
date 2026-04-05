from db import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=== FRANCHISE SQUADS ===")
teams = [
    "Chennai Super Kings", "Mumbai Indians", "Royal Challengers Bengaluru",
    "Kolkata Knight Riders", "Rajasthan Royals", "Delhi Capitals",
    "Punjab Kings", "Sunrisers Hyderabad", "Gujarat Titans", "Lucknow Super Giants"
]
for t in teams:
    count = db.execute(text(
        "SELECT COUNT(*) FROM players WHERE franchise_team_id = (SELECT team_id FROM teams WHERE name LIKE :n LIMIT 1)"
    ), {"n": f"%{t}%"}).scalar()
    print(f"  {t}: {count} players")

print("\n=== INTERNATIONAL SQUADS ===")
countries = ["India", "Australia", "England", "Pakistan", "South Africa", "New Zealand"]
for c in countries:
    count = db.execute(text(
        "SELECT COUNT(*) FROM players WHERE intl_team_id = (SELECT team_id FROM teams WHERE name = :n LIMIT 1)"
    ), {"n": c}).scalar()
    print(f"  {c}: {count} players")

print("\n=== SPOT CHECK: Virat Kohli ===")
row = db.execute(text(
    "SELECT p.name, p.role, p.batting_style, p.nationality, "
    "t1.name as franchise, t2.name as intl_team "
    "FROM players p "
    "LEFT JOIN teams t1 ON p.franchise_team_id = t1.team_id "
    "LEFT JOIN teams t2 ON p.intl_team_id = t2.team_id "
    "WHERE p.name LIKE '%Virat Kohli%'"
)).fetchone()
if row:
    print(f"  Name: {row[0]}")
    print(f"  Role: {row[1]}, Bat: {row[2]}")
    print(f"  Franchise: {row[4]}")
    print(f"  International: {row[5]}")

print("\n=== LOGOS ===")
logos = db.execute(text("SELECT name, logo_path FROM teams WHERE logo_path IS NOT NULL")).fetchall()
print(f"  Total teams with logos: {len(logos)}")
for l in logos:
    print(f"    {l[0]}: {l[1]}")

db.close()
