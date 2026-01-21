import sqlite3

def create_and_populate_cars_table(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Create cars table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY,
            car_type TEXT,
            city TEXT,
            price REAL,
            available_from TEXT,
            available_to TEXT
        )
    ''')
    # Insert sample data
    cars = [
        (1, 'SUV', 'London', 100.0, '2026-01-20', '2026-01-27'),
        (2, 'SEDAN', 'London', 80.0, '2026-01-20', '2026-01-27'),
        (3, 'TRUCK', 'London', 120.0, '2026-01-20', '2026-01-27')
    ]
    cur.executemany('INSERT OR IGNORE INTO cars VALUES (?, ?, ?, ?, ?, ?)', cars)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_and_populate_cars_table("travel_agency.db")
    print("Cars table created and populated.")
