import requests

def test_open_meteo(city):
    print(f"Testing Open-Meteo for {city}...")
    try:
        # Step 1: Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url, timeout=5)
        if geo_resp.status_code == 200 and 'results' in geo_resp.json():
            location = geo_resp.json()['results'][0]
            lat, lon = location['latitude'], location['longitude']
            
            # Step 2: Weather
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_resp = requests.get(weather_url, timeout=5)
            
            if weather_resp.status_code == 200:
                data = weather_resp.json()
                current = data['current_weather']
                
                # Open-Meteo WMO weather codes mapped to descriptions
                wmo_codes = {
                    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                    45: "Fog", 48: "Depositing rime fog",
                    51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
                    61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
                    71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow",
                    80: "Slight Rain showers", 81: "Moderate Rain showers", 82: "Violent Rain showers",
                    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
                }
                condition = wmo_codes.get(current['weathercode'], "Unknown Weather")
                
                print({
                    "temp": f"{current['temperature']}°C",
                    "condition": condition,
                    "humidity": "N/A", # Open-Meteo current_weather doesn't include humidity by default
                    "source": "Open-Meteo"
                })
                return
        print("Failed to get weather")
    except Exception as e:
        print("Error:", e)

test_open_meteo("Mumbai")
test_open_meteo("London")
