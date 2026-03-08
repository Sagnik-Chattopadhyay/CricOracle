import requests

payload = {
    "team_a": "India",
    "team_b": "New Zealand",
    "venue": "Wankhede Stadium",
    "match_format": "T20I"
}

resp = requests.post("http://localhost:8000/predict", json=payload)
if resp.status_code == 200:
    data = resp.json()
    print("Weather found:", data.get('weather'))
else:
    print("Prediction failed:", resp.text)
