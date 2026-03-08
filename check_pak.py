from sqlalchemy import create_engine, or_, and_, desc, func
from sqlalchemy.orm import sessionmaker
from models import Team, Match, Delivery, Player

engine = create_engine("sqlite:///e:/projects/cricmatch_predict/cricpredict.db")
Session = sessionmaker(bind=engine)
db = Session()

def check_team_players(team_name, match_format):
    print(f"Checking for team: {team_name} in format: {match_format}")
    team = db.query(Team).filter(Team.name.ilike(f"%{team_name}%")).first()
    if not team:
        print("Team not found")
        return

    last_match = db.query(Match).filter(
        (Match.team_a_id == team.team_id) | (Match.team_b_id == team.team_id)
    ).filter(Match.format == match_format).order_by(desc(Match.date)).first()

    if not last_match:
        print("No matches found")
        return

    print(f"Last match: {last_match.match_id} on {last_match.date}")

    # Check batsmen
    batsmen_ids = db.query(Delivery.batsman_id).filter(
        Delivery.match_id == last_match.match_id,
        Delivery.batting_team_id == team.team_id
    ).distinct().all()

    for (p_id,) in batsmen_ids:
        player = db.query(Player).filter(Player.player_id == p_id).first()
        if not player:
            print(f"MISSING BATSMAN: player_id {p_id} not found in Player table!")
        else:
            print(f"Batsman {p_id}: {player.name}")

    # Check bowlers
    bowlers_ids = db.query(Delivery.bowler_id).filter(
        Delivery.match_id == last_match.match_id,
        Delivery.bowling_team_id == team.team_id
    ).distinct().all()

    for (p_id,) in bowlers_ids:
        player = db.query(Player).filter(Player.player_id == p_id).first()
        if not player:
            print(f"MISSING BOWLER: player_id {p_id} not found in Player table!")
        else:
            print(f"Bowler {p_id}: {player.name}")

check_team_players("Pakistan", "T20I")
db.close()
