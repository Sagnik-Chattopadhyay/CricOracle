from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db import SessionLocal
from scorer import MatchScorer
from real_time_sync import sync_recent_matches
from pydantic import BaseModel
import os
import requests
from typing import Optional, List, Dict
from models import Team, Venue
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CricPredict API", description="AI-powered cricket match predictions")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PredictionRequest(BaseModel):
    team_a: str
    team_b: str
    venue: str
    match_format: Optional[str] = "IPL"

@app.get("/")
def read_root():
    return {"message": "Welcome to CricPredict API. Use /predict for match predictions."}

def get_weather(city: str) -> Dict:
    """Fetch weather forecast for the match city."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if api_key:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "temp": f"{data['main']['temp']}°C",
                    "condition": data['weather'][0]['description'].title(),
                    "humidity": f"{data['main']['humidity']}%",
                    "source": "OpenWeather"
                }
        except:
            pass
            
    # Fallback to Open-Meteo (No key required)
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url, timeout=5)
        if geo_resp.status_code == 200 and 'results' in geo_resp.json():
            location = geo_resp.json()['results'][0]
            lat, lon = location['latitude'], location['longitude']
            
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_resp = requests.get(weather_url, timeout=5)
            
            if weather_resp.status_code == 200:
                data = weather_resp.json()
                current = data['current_weather']
                
                wmo_codes = {
                    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                    45: "Fog", 48: "Depositing rime fog",
                    51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
                    61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
                    71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow",
                    80: "Slight Rain showers", 81: "Moderate showers", 82: "Violent showers",
                    95: "Thunderstorm", 96: "Thunderstorm, light hail", 99: "Thunderstorm, heavy hail"
                }
                condition = wmo_codes.get(current['weathercode'], "Unknown Weather")
                
                return {
                    "temp": f"{current['temperature']}°C",
                    "condition": condition,
                    "humidity": "N/A",
                    "source": "Open-Meteo"
                }
    except:
        pass
        
    return {"condition": "Conditions Unknown", "temp": "N/A", "humidity": "N/A", "source": "None"}

@app.post("/predict")
def predict(request: PredictionRequest, db: Session = Depends(get_db)):
    scorer = MatchScorer(db)
    result = scorer.predict_match(
        request.team_a, 
        request.team_b, 
        request.venue, 
        request.match_format
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    # Add weather if venue city is known
    city = result.get("venue", {}).get("city")
    if city and city != "Unknown":
        result["weather"] = get_weather(city)
    else:
        result["weather"] = {"condition": "Venue City Unknown", "temp": "N/A", "humidity": "N/A", "source": "None"}
        
    return result
@app.get("/team/last-match")
def get_team_last_match(team: str, format: str = "IPL", db: Session = Depends(get_db)):
    scorer = MatchScorer(db)
    result = scorer.get_team_last_match(team, format)
    if not result:
        raise HTTPException(status_code=404, detail="Last match not found for this team and format.")
    return result

@app.get("/team/h2h-details")
def get_h2h_details(team_a: str, team_b: str, format: str = "IPL", limit: int = 5, db: Session = Depends(get_db)):
    scorer = MatchScorer(db)
    result = scorer.get_detailed_h2h_matches(team_a, team_b, format, limit)
    if isinstance(result, tuple) and "error" in result[0]:
        raise HTTPException(status_code=404, detail=result[0]["error"])
    return result
@app.get("/search/teams", response_model=List[str])
def search_teams(q: str, format: Optional[str] = None, db: Session = Depends(get_db)):
    """Search for teams by name (case-insensitive) with format-specific filtering."""
    query = db.query(Team).filter(Team.name.ilike(f"%{q}%"))
    
    if format == 'IPL':
        query = query.filter(Team.team_type == 'Franchise')
    elif format in ['T20I', 'ODI', 'Tests']:
        query = query.filter(Team.team_type == 'International')
        
    teams = query.limit(10).all()
    return [t.name for t in teams]

@app.get("/venues/countries", response_model=List[str])
def get_venue_countries(db: Session = Depends(get_db)):
    """Get unique countries that have venues in the database."""
    countries = db.query(Venue.country).filter(Venue.country != None).distinct().all()
    return sorted([c[0] for c in countries])

@app.get("/venues/by-country", response_model=List[str])
def get_venues_by_country(country: str, db: Session = Depends(get_db)):
    """Get all stadiums in a specific country."""
    venues = db.query(Venue).filter(Venue.country == country).all()
    return sorted([v.name for v in venues])

@app.post("/sync")
def trigger_sync():
    """Manually trigger the live data sync."""
    try:
        sync_recent_matches()
        return {"status": "success", "message": "Live data sync completed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
