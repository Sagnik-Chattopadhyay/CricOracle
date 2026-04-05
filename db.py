import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# We'll use environment variables for security
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    # Use SQLite for local development by default if no DATABASE_URL is set
    DB_URL = "sqlite:///./cricpredict.db"
    print(f"Warning: DATABASE_URL not found. Using local SQLite: {DB_URL}")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_canonical_team_name(name: str) -> str:
    """
    Maps historical or alternative team names to their current canonical versions.
    Used for merging rebranded franchises (e.g. RCB, Delhi Capitals, Punjab Kings).
    """
    if not name:
        return name
        
    mapping = {
        # IPL Re-brands (Canonical: Latest Name)
        "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
        "Royal Challengers": "Royal Challengers Bengaluru",
        "RCB": "Royal Challengers Bengaluru",
        "Bangalore": "Royal Challengers Bengaluru",
        "Delhi Daredevils": "Delhi Capitals",
        "Delhi": "Delhi Capitals",
        "Kings XI Punjab": "Punjab Kings",
        "PBKS": "Punjab Kings",
        "Punjab": "Punjab Kings",
        "Rising Pune Supergiants": "Rising Pune Supergiant",
        "RPS": "Rising Pune Supergiant",
        "Rising Pune Supergiant": "Rising Pune Supergiant",
        "Deccan Chargers": "Sunrisers Hyderabad", # Historically replaced by SRH
        "Mumbai": "Mumbai Indians",
        "Kolkata": "Kolkata Knight Riders",
        "KKR": "Kolkata Knight Riders",
        "Chennai": "Chennai Super Kings",
        "CSK": "Chennai Super Kings",
        "Rajasthan": "Rajasthan Royals",
        "RR": "Rajasthan Royals",
        "Hyderabad": "Sunrisers Hyderabad",
        "SRH": "Sunrisers Hyderabad",
        "Gujarat": "Gujarat Titans", # GT is default for 'Gujarat' now
        "GT": "Gujarat Titans",
        "Lucknow": "Lucknow Super Giants",
        "LSG": "Lucknow Super Giants",
    }

    
    return mapping.get(name, name)

