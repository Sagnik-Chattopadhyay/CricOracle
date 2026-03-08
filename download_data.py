import requests
import zipfile
import io
import os

def download_and_extract(url, extract_to):
    print(f"Downloading from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(extract_to)
        print(f"Successfully extracted to {extract_to}")
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")

if __name__ == "__main__":
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Cricsheet CSV format 2 (experimental) links
    urls = {
        "IPL": "https://cricsheet.org/downloads/ipl_male_csv2.zip",
        "T20I": "https://cricsheet.org/downloads/t20s_male_csv2.zip",
        "ODI": "https://cricsheet.org/downloads/odis_male_csv2.zip",
        "Tests": "https://cricsheet.org/downloads/tests_male_csv2.zip"
    }
    
    for league, url in urls.items():
        league_dir = os.path.join(data_dir, league)
        os.makedirs(league_dir, exist_ok=True)
        
        # Skip if already has files (roughly)
        if len(os.listdir(league_dir)) > 10:
            print(f"Skipping {league} as it already contains data.")
            continue
            
        download_and_extract(url, league_dir)
