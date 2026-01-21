import sqlite3

def print_db_contents(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    print("\nFlights:")
    for row in cur.execute("SELECT * FROM flights;"):
        print(row)
    print("\nHotels:")
    for row in cur.execute("SELECT * FROM hotels;"):
        print(row)
    print("\nCars:")
    for row in cur.execute("SELECT * FROM cars;"):
        print(row)
    conn.close()

if __name__ == "__main__":
    print_db_contents("travel_agency.db")
