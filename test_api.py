import requests
resp = requests.get('http://localhost:8000/team/h2h-details?team_a=India&team_b=New%20Zealand&format=T20I&limit=5')
print(resp.status_code)
if resp.status_code == 200:
    for m in resp.json():
        print(f"{m['date']} | {m['match_title']}")
else:
    print(resp.text)
