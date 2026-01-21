"""Check what's actually in the travel database"""
import sqlite3

db_path = "src/a2a_mcp/mcp/travel_agency.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== DATABASE TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for t in tables:
    print(f"  {t[0]}")
    cursor.execute(f"SELECT * FROM {t[0]} LIMIT 3")
    rows = cursor.fetchall()
    if rows:
        print(f"    Sample: {len(rows)} rows shown")
        for row in rows[:1]:
            print(f"    {row}")
    print()

conn.close()
