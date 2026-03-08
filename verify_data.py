from db import SessionLocal
from models import Match, Team, Player, Venue, Delivery
from sqlalchemy import func

def verify():
    db = SessionLocal()
    
    match_count = db.query(Match).count()
    team_count = db.query(Team).count()
    player_count = db.query(Player).count()
    venue_count = db.query(Venue).count()
    delivery_count = db.query(Delivery).count()
    
    print("--- Database Verification ---")
    print(f"Total Matches:   {match_count}")
    print(f"Total Teams:     {team_count}")
    print(f"Total Players:   {player_count}")
    print(f"Total Venues:    {venue_count}")
    print(f"Total Deliveries: {delivery_count}")
    
    print("\n--- Match Breakdown by Format ---")
    formats = db.query(Match.format, func.count(Match.match_id)).group_by(Match.format).all()
    for f, count in formats:
        print(f"{f}: {count}")

    print("\n--- Sample Delivery ---")
    sample = db.query(Delivery).first()
    if sample:
        match = db.query(Match).filter_by(match_id=sample.match_id).first()
        batting_team = db.query(Team).filter_by(team_id=sample.batting_team_id).first()
        bowler = db.query(Player).filter_by(player_id=sample.bowler_id).first()
        batsman = db.query(Player).filter_by(player_id=sample.batsman_id).first()
        
        print(f"Match: {match.date} - {batting_team.name}")
        print(f"Over {sample.over}.{sample.ball}: {bowler.name} to {batsman.name}, {sample.runs_off_bat} runs")
    
    db.close()

if __name__ == "__main__":
    verify()
