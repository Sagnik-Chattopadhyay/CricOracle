from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scorer import MatchScorer
from db import SessionLocal

engine = create_engine("sqlite:///e:/projects/cricmatch_predict/cricpredict.db")
Session = sessionmaker(bind=engine)
db = Session()

scorer = MatchScorer(db)
print("Testing get_team_last_match for Pakistan...")
try:
    result = scorer.get_team_last_match("Pakistan", "T20I")
    print("SUCCESS!")
    print(f"Match: {result['match_title']}")
    print(f"Top Batsman: {result['top_batsmen'][0]['name'] if result['top_batsmen'] else 'None'}")
except Exception as e:
    print(f"FAILED with error: {e}")
    import traceback
    traceback.print_exc()

db.close()
