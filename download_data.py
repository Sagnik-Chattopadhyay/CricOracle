import requests
import zipfile
import io
import os
import sys
import shutil

def download_and_extract(url, extract_to, force=False):
    print(f"Downloading from {url}...")
    
    if force and os.path.exists(extract_to):
        print(f"  Force mode: clearing old data in {extract_to}...")
        shutil.rmtree(extract_to)
        os.makedirs(extract_to, exist_ok=True)
    
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(extract_to)
        print(f"Successfully extracted to {extract_to}")
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")

if __name__ == "__main__":
    force = "--force" in sys.argv
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
        
        # Skip if already has files (unless --force is used)
        if not force and len(os.listdir(league_dir)) > 10:
            print(f"Skipping {league} as it already contains data. Use --force to re-download.")
            continue
            
        download_and_extract(url, league_dir, force=force)
