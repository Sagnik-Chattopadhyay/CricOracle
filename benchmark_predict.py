import requests
import time

payload = {
    "team_a": "India",
    "team_b": "New Zealand",
    "venue": "Wankhede Stadium",
    "match_format": "T20I"
}

print("Running cold start prediction test...")
start = time.time()
resp = requests.post("http://localhost:8000/predict", json=payload)
end = time.time()
if resp.status_code == 200:
    print(f"Success! Prediction calculated in {end - start:.2f} seconds.")
else:
    print("Prediction failed:", resp.text)
