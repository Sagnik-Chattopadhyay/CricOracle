import requests

def test_weather(city):
    print(f"Testing wttr.in for {city}...")
    try:
        url = f"https://wttr.in/{city}?format=j1"
        resp = requests.get(url, timeout=5)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            current = data['current_condition'][0]
            print({
                "temp": f"{current['temp_C']}°C",
                "condition": current['weatherDesc'][0]['value'],
                "humidity": f"{current['humidity']}%",
                "source": "wttr.in"
            })
        else:
            print("Response:", resp.text)
    except Exception as e:
        print("Error:", e)

test_weather("Mumbai")
test_weather("Wankhede Stadium")
