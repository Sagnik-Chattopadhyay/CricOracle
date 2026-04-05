import sqlite3

def migrate():
    conn = sqlite3.connect('cricpredict.db')
    cursor = conn.cursor()
    
    print("=== DATABASE MIGRATION V2 (2026 REFRESH) ===")
    
    # 1. Add logo_path to teams if missing
    try:
        cursor.execute("ALTER TABLE teams ADD COLUMN logo_path TEXT")
        print(" [OK] Added logo_path to teams table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(" [SKIP] logo_path already exists in teams table.")
        else:
            print(f" [ERR] teams table error: {e}")

    # 2. Add intl_team_id and franchise_team_id to players
    for col in ["intl_team_id", "franchise_team_id"]:
        try:
            cursor.execute(f"ALTER TABLE players ADD COLUMN {col} INTEGER REFERENCES teams(team_id)")
            print(f" [OK] Added {col} to players table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f" [SKIP] {col} already exists in players table.")
            else:
                print(f" [ERR] players table error for {col}: {e}")

    conn.commit()
    conn.close()
    print("=== MIGRATION COMPLETE ===")

if __name__ == "__main__":
    migrate()
