from db import SessionLocal, get_canonical_team_name
from scorer import MatchScorer
from models import Team

db = SessionLocal()
scorer = MatchScorer(db)

print("=== 1. Utility function check ===")
print(f"Bangalore -> {get_canonical_team_name('Royal Challengers Bangalore')}")
print(f"Delhi DD -> {get_canonical_team_name('Delhi Daredevils')}")
print(f"Punjab KXIP -> {get_canonical_team_name('Kings XI Punjab')}")
print(f"Bengaluru -> {get_canonical_team_name('Royal Challengers Bengaluru')}")

print("\n=== 2. Scorer lookup check ===")
# Exact match of historical name
team_blore = scorer.predict_match('Royal Challengers Bangalore', 'Mumbai Indians', 'Wankhede Stadium', 'IPL')
if 'error' not in team_blore:
    print(f"Found RCB via 'Bangalore' name! Canonical name in DB: {team_blore['team_a']['name']}")
else:
    print(f"FAILED: Could not find RCB via 'Bangalore' name. Error: {team_blore['error']}")

# Fuzzy match of historical name (Bangalore)
# find_team inside predict_match uses get_canonical_team_name(name) then searches.
# If I pass 'Bangalore' it won't map unless it's exactly one of the keys.
# But part of 'find_team' is a fuzzy search: ilike(f'%{name}%')
# 'Bangalore' is not in 'Royal Challengers Bengaluru'.
# So searching for 'Bangalore' will fail unless it's in the mapping.

print("\n=== 3. Mapping for partial names? ===")
# Should we add partial mappings? Probably better to just handle the full official names.
# If someone types 'Bangalore' maybe it should still work.
# Let's see if we should add "Bangalore" to the mapping.

db.close()
