#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# --- Optional: Database Setup ---
# Uncomment and modify if you want to download a pre-built database from a URL
# if [ ! -f cricpredict.db ]; then
#   echo "Downloading database..."
#   curl -L -o cricpredict.db "YOUR_DIRECT_DOWNLOAD_LINK_HERE"
# fi

# Run any necessary setup scripts
# python add_indexes.py
