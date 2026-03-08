from db import SessionLocal
from models import Match, Delivery, Player, Team
from sqlalchemy import desc

def fetch_squad(team_name, format="T20I"):
    db = SessionLocal()
    team = db.query(Team).filter(Team.name == team_name).first()
    if not team:
        print("Team not found")
        return
        
    # Get last 3 matches to build a solid squad
    recent_matches = db.query(Match).filter(
        (Match.team_a_id == team.team_id) | (Match.team_b_id == team.team_id)
    ).filter(Match.format == format).order_by(desc(Match.date)).limit(3).all()
    
    match_ids = [m.match_id for m in recent_matches]
    if not match_ids:
        print("No recent matches")
        return
        
    # Batsmen and non-strikers (when team is batting)
    batters = db.query(Delivery.batsman_id).filter(
        Delivery.match_id.in_(match_ids), Delivery.batting_team_id == team.team_id
    ).distinct().all()
    
    non_strikers = db.query(Delivery.non_striker_id).filter(
        Delivery.match_id.in_(match_ids), Delivery.batting_team_id == team.team_id
    ).distinct().all()
    
    # Bowlers (when team is bowling)
    bowlers = db.query(Delivery.bowler_id).filter(
        Delivery.match_id.in_(match_ids), Delivery.bowling_team_id == team.team_id
    ).distinct().all()
    
    all_player_ids = set([p[0] for p in batters] + [p[0] for p in non_strikers] + [p[0] for p in bowlers])
    
    players = db.query(Player).filter(Player.player_id.in_(all_player_ids)).all()
    print(f"Squad for {team_name} (Format: {format}):")
    for p in players:
        print(f"- {p.name}")
    print(f"Total: {len(players)}")
    db.close()

if __name__ == "__main__":
    fetch_squad("New Zealand", "T20I")
