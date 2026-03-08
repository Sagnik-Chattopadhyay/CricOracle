import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class CricketDataAPI:
    """
    Interface for CricketData.org API.
    Handles real-time match lists and scorecards.
    """
    BASE_URL = "https://api.cricapi.com/v1"
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("CRICKET_API_KEY")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        if not self.api_key:
            print("Warning: No API Key found. Set CRICKET_API_KEY in your .env file.")

    def get_current_matches(self):
        """Fetches list of currently ongoing or recently finished matches."""
        url = f"{self.BASE_URL}/currentMatches?apikey={self.api_key}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching matches: {e}")
            return None

    def get_match_scorecard(self, match_id):
        """Fetches detailed scorecard for a specific match ID."""
        url = f"{self.BASE_URL}/match_scorecard?apikey={self.api_key}&id={match_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching scorecard for {match_id}: {e}")
            return None

if __name__ == "__main__":
    # Test block (requires API key in .env)
    api = CricketDataAPI()
    matches = api.get_current_matches()
    if matches:
        print(f"Found {len(matches.get('data', []))} current matches.")
    else:
        print("Could not retrieve matches. Check your API key.")
