from db import SessionLocal
from models import Player

db = SessionLocal()
players = db.query(Player).filter(Player.name.in_(['HH Pandya', 'SA Yadav', 'JJ Bumrah', 'V Kohli'])).all()
for p in players:
    print(f"{p.name}: Role={p.role}, Bat={p.batting_style}, Bowl={p.bowling_style}")
db.close()
