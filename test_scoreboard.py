from db import SessionLocal
from models import Match, Delivery, Team, Player, Venue
from sqlalchemy import desc, func

def get_last_match_scoreboard(team_name, format="T20I"):
    db = SessionLocal()
    team = db.query(Team).filter(Team.name == team_name).first()
    if not team:
        print("Team not found")
        return
        
    last_match = db.query(Match).filter(
        (Match.team_a_id == team.team_id) | (Match.team_b_id == team.team_id)
    ).filter(Match.format == format).order_by(desc(Match.date)).first()
    
    if not last_match:
        print("No match found")
        return
        
    team_a = db.query(Team).filter(Team.team_id == last_match.team_a_id).first()
    team_b = db.query(Team).filter(Team.team_id == last_match.team_b_id).first()
    venue = db.query(Venue).filter(Venue.venue_id == last_match.venue_id).first()
    winner = db.query(Team).filter(Team.team_id == last_match.winner_id).first()
    
    print(f"Match: {team_a.name} vs {team_b.name}")
    print(f"Date: {last_match.date}, Venue: {venue.name}, {venue.city}")
    print(f"Result: {winner.name if winner else 'Draw'} won by {last_match.win_margin}")
    
    # Calculate scores
    scores = db.query(
        Delivery.batting_team_id,
        func.sum(Delivery.runs_off_bat + Delivery.extras).label("total_runs"),
        func.count(Delivery.player_dismissed_id).label("wickets"),
        func.max(Delivery.over).label("overs")
    ).filter(Delivery.match_id == last_match.match_id).group_by(Delivery.batting_team_id).all()
    
    for score in scores:
        t_name = db.query(Team).filter(Team.team_id == score.batting_team_id).first().name
        overs = f"{score.overs}.{db.query(Delivery).filter(Delivery.match_id == last_match.match_id, Delivery.batting_team_id == score.batting_team_id, Delivery.over == score.overs).count()}"
        print(f"{t_name}: {score.total_runs}/{score.wickets} ({overs} ov)")
        
    db.close()

if __name__ == "__main__":
    get_last_match_scoreboard("India", "T20I")
