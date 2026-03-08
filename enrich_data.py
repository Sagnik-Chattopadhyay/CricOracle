from db import SessionLocal, engine
from models import Team, Venue, Match, Base

def enrich_data():
    # Update schema
    Base.metadata.create_all(engine)
    db = SessionLocal()
    
    print("Enriching Team types...")
    # Get all teams that played in IPL
    ipl_teams_query = db.query(Team.team_id).join(Match, (Match.team_a_id == Team.team_id) | (Match.team_b_id == Team.team_id)).filter(Match.format == 'IPL').distinct()
    ipl_team_ids = [r[0] for r in ipl_teams_query.all()]
    
    db.query(Team).filter(Team.team_id.in_(ipl_team_ids)).update({Team.team_type: 'Franchise'}, synchronize_session=False)
    db.query(Team).filter(~Team.team_id.in_(ipl_team_ids)).update({Team.team_type: 'International'}, synchronize_session=False)
    
    print("Enriching Venue countries...")
    # Basic mapping for venues by city/name hints
    # This is a heuristic. For professional apps, we'd use a geomapping API.
    venue_country_map = {
        'India': ['Mumbai', 'Bangalore', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Ahmedabad', 'Pune', 'Jaipur', 'Mohali', 'Dharamsala', 'Indore', 'Lucknow', 'Guwahati', 'Visakhapatnam', 'Cuttack', 'Nagpur', 'Ranchi', 'Rajkot', 'Kanpur'],
        'United Arab Emirates': ['Dubai', 'Abu Dhabi', 'Sharjah'],
        'South Africa': ['Cape Town', 'Johannesburg', 'Durban', 'Centurion', 'Port Elizabeth', 'Bloemfontein', 'East London'],
        'England': ['London', 'Birmingham', 'Manchester', 'Nottingham', 'Leeds', 'Southampton', 'Cardiff', 'Bristol'],
        'Australia': ['Melbourne', 'Sydney', 'Brisbane', 'Perth', 'Adelaide', 'Hobart', 'Canberra', 'Gold Coast', 'Geelong'],
        'New Zealand': ['Auckland', 'Wellington', 'Christchurch', 'Hamilton', 'Dunedin', 'Mount Maunganui', 'Napier', 'Nelson'],
        'West Indies': ['St Kitts', 'Barbados', 'Guyana', 'Trinidad', 'Antigua', 'Jamaica', 'St Lucia', 'Grenada'],
        'Sri Lanka': ['Colombo', 'Kandy', 'Galle', 'Hambantota', 'Dambulla'],
        'Pakistan': ['Lahore', 'Karachi', 'Rawalpindi', 'Multan'],
        'Bangladesh': ['Dhaka', 'Chittagong', 'Sylhet'],
        'Zimbabwe': ['Harare', 'Bulawayo']
    }
    
    venues = db.query(Venue).all()
    for v in venues:
        # Check city first
        assigned = False
        for country, cities in venue_country_map.items():
            if v.city and any(city in v.city for city in cities):
                v.country = country
                assigned = True
                break
            if any(city in v.name for city in cities):
                v.country = country
                assigned = True
                break
        
        if not assigned:
            # Default to India if it's an IPL venue and city is missing
            v.country = "India"
            
    db.commit()
    print("Enrichment complete.")
    db.close()

if __name__ == "__main__":
    enrich_data()
