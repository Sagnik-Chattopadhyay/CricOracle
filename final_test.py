from db import SessionLocal
from scorer import MatchScorer

def final_test():
    db = SessionLocal()
    scorer = MatchScorer(db)
    
    print("Testing International Match: India vs England")
    res = scorer.predict_match('India', 'England', 'Adelaide Oval', 'ODI')
    
    if "error" in res:
        print(f"Error: {res['error']}")
    else:
        print(f"Team A: {res['team_a']['name']}")
        print(f"Team B: {res['team_b']['name']}")
        print(f"Squad A Count: {len(res['team_a']['squad'])}")
        print(f"H2H Matches: {res['h2h']['total']}")
        print(f"Win Probability: {res['win_probability']} for {res['prediction']}")
    
    db.close()

if __name__ == "__main__":
    final_test()
