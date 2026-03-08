import requests
import json

def test():
    resp = requests.get("http://localhost:8000/team/last-match?team=India&format=T20I")
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    test()
