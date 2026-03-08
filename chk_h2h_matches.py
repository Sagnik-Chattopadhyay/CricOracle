from db import SessionLocal
from models import Match, Team
from sqlalchemy import or_, and_, desc

db = SessionLocal()

team_a = db.query(Team).filter(Team.name == 'India').first()
team_b = db.query(Team).filter(Team.name == 'New Zealand').first()

print(f"Team A: {team_a.name} ({team_a.team_id})")
print(f"Team B: {team_b.name} ({team_b.team_id})")

h2h_matches = (
    db.query(Match)
    .filter(Match.format == 'T20I')
    .filter(
        or_(
            and_(Match.team_a_id == team_a.team_id, Match.team_b_id == team_b.team_id),
            and_(Match.team_a_id == team_b.team_id, Match.team_b_id == team_a.team_id)
        )
    )
    .order_by(desc(Match.date))
    .limit(5)
    .all()
)
print(f"Found matches: {len(h2h_matches)}")
for m in h2h_matches:
    print(f"- {m.date} | Format: {m.format}")

db.close()
