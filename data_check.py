import pandas as pd
import os

def check_csv_quality(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False
    
    try:
        df = pd.read_csv(file_path)
        print(f"--- Analysis for {os.path.basename(file_path)} ---")
        print(f"Total Rows: {len(df)}")
        print(f"Columns: {', '.join(df.columns)}")
        print("\nMissing Values:")
        print(df.isnull().sum())
        
        # Check for critical columns (example for IPL deliveries)
        critical_cols = ['match_id', 'innings', 'batting_team', 'bowling_team', 'striker', 'bowler', 'runs_off_bat']
        missing_critical = [col for col in critical_cols if col not in df.columns]
        
        if missing_critical:
            print(f"\nWarning: Missing critical columns for prediction: {missing_critical}")
        else:
            print("\nAll critical columns found.")
            
        return True
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage - user will need to provide the actual paths
    data_dir = "data"
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
        for file in files:
            check_csv_quality(os.path.join(data_dir, file))
    else:
        print(f"Please create a '{data_dir}' folder and place your Kaggle/Cricsheet CSV files there.")
