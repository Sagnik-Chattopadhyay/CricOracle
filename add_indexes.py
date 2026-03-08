import sqlite3

conn = sqlite3.connect('cricpredict.db')
cursor = conn.cursor()

print("Creating indexes...")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_delivery_match ON deliveries(match_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_delivery_batsman ON deliveries(batsman_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_delivery_bowler ON deliveries(bowler_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_match_format ON matches(format);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_match_date ON matches(date);")

conn.commit()
conn.close()
print("Done!")
