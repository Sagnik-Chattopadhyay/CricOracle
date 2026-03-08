from db import SessionLocal
from models import Match, Team
from sqlalchemy import or_, and_

db = SessionLocal()

team_a = db.query(Team).filter(Team.name == 'India').first()
team_b = db.query(Team).filter(Team.name == 'New Zealand').first()

all_matches = (
    db.query(Match)
    .filter(
        or_(
            and_(Match.team_a_id == team_a.team_id, Match.team_b_id == team_b.team_id),
            and_(Match.team_a_id == team_b.team_id, Match.team_b_id == team_a.team_id)
        )
    )
    .all()
)

print(f"Total Matches: {len(all_matches)}")
for format in ['T20I', 'ODI', 'Tests', 'IPL', 'T20 International']:
    matches_fmt = [m for m in all_matches if m.format == format]
    print(f" - {format}: {len(matches_fmt)}")

db.close()
