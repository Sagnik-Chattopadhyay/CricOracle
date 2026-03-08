from db import SessionLocal
from models import Venue

def fix_venue_cities():
    db = SessionLocal()
    venues = db.query(Venue).filter((Venue.city == '') | (Venue.city == None)).all()
    print(f"Checking {len(venues)} venues for missing city data...")
    
    fixes = {
        'adelaide': 'Adelaide',
        'sydney': 'Sydney',
        'melbourne': 'Melbourne',
        'wankhede': 'Mumbai',
        'chinnaswamy': 'Bengaluru',
        'gabba': 'Brisbane',
        'perth': 'Perth',
        'eden gardens': 'Kolkata',
        'feroz shah kotla': 'Delhi',
        'arun jaitley': 'Delhi',
        'bellerive': 'Hobart',
        'manuka': 'Canberra',
        'm.a. chidambaram': 'Chennai',
        'rajiv gandhi': 'Hyderabad',
        'sawai mansingh': 'Jaipur',
        'narendra modi': 'Ahmedabad',
        'motera': 'Ahmedabad'
    }
    
    fixed_count = 0
    for v in venues:
        name_lower = v.name.lower()
        for key, city in fixes.items():
            if key in name_lower:
                v.city = city
                fixed_count += 1
                break
                
    db.commit()
    print(f"Fixed {fixed_count} venues.")
    db.close()

if __name__ == "__main__":
    fix_venue_cities()
