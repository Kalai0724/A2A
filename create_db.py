import sqlite3

conn = sqlite3.connect('travel_agency.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number TEXT,
    airline TEXT,
    origin TEXT,
    destination TEXT,
    date TEXT,
    travel_class TEXT,
    cost REAL
)''')

c.execute('''CREATE TABLE hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    city TEXT,
    room_type TEXT,
    price_per_night REAL,
    available_from TEXT,
    available_to TEXT
)''')

c.execute('''CREATE TABLE rental_cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT,
    city TEXT,
    car_type TEXT,
    price REAL,
    available_from TEXT,
    available_to TEXT
)''')

# Insert demo data
c.execute("INSERT INTO flights (flight_number, airline, origin, destination, date, travel_class, cost) VALUES ('BA286', 'British Airways', 'San Francisco', 'London', '2026-01-20', 'ECONOMY', 800.00)")
c.execute("INSERT INTO flights (flight_number, airline, origin, destination, date, travel_class, cost) VALUES ('BA287', 'British Airways', 'London', 'San Francisco', '2026-01-27', 'ECONOMY', 800.00)")
c.execute("INSERT INTO hotels (name, city, room_type, price_per_night, available_from, available_to) VALUES ('London Grand Hotel', 'London', 'STANDARD', 200.00, '2026-01-20', '2026-01-27')")
c.execute("INSERT INTO rental_cars (provider, city, car_type, price, available_from, available_to) VALUES ('Hertz', 'London', 'SUV', 350.00, '2026-01-20', '2026-01-27')")

# Additional demo data for more coverage
# Flights
c.execute("INSERT INTO flights (flight_number, airline, origin, destination, date, travel_class, cost) VALUES ('UA100', 'United Airlines', 'San Francisco', 'London', '2026-01-20', 'BUSINESS', 1500.00)")
c.execute("INSERT INTO flights (flight_number, airline, origin, destination, date, travel_class, cost) VALUES ('UA101', 'United Airlines', 'London', 'San Francisco', '2026-01-27', 'BUSINESS', 1500.00)")
c.execute("INSERT INTO flights (flight_number, airline, origin, destination, date, travel_class, cost) VALUES ('AA200', 'American Airlines', 'San Francisco', 'London', '2026-01-20', 'ECONOMY', 750.00)")
c.execute("INSERT INTO flights (flight_number, airline, origin, destination, date, travel_class, cost) VALUES ('AA201', 'American Airlines', 'London', 'San Francisco', '2026-01-27', 'ECONOMY', 750.00)")
# Hotels
c.execute("INSERT INTO hotels (name, city, room_type, price_per_night, available_from, available_to) VALUES ('London Luxury Suites', 'London', 'DELUXE', 400.00, '2026-01-20', '2026-01-27')")
# Add a SUITE room for London
c.execute("INSERT INTO hotels (name, city, room_type, price_per_night, available_from, available_to) VALUES ('London Royal Suite', 'London', 'SUITE', 600.00, '2026-01-20', '2026-01-27')")
c.execute("INSERT INTO hotels (name, city, room_type, price_per_night, available_from, available_to) VALUES ('London Budget Inn', 'London', 'STANDARD', 120.00, '2026-01-20', '2026-01-27')")
# Rental Cars
c.execute("INSERT INTO rental_cars (provider, city, car_type, price, available_from, available_to) VALUES ('Avis', 'London', 'TRUCK', 500.00, '2026-01-20', '2026-01-27')")
c.execute("INSERT INTO rental_cars (provider, city, car_type, price, available_from, available_to) VALUES ('Enterprise', 'London', 'SEDAN', 250.00, '2026-01-20', '2026-01-27')")
c.execute("INSERT INTO rental_cars (provider, city, car_type, price, available_from, available_to) VALUES ('Budget', 'London', 'SUV', 300.00, '2026-01-20', '2026-01-27')")

conn.commit()
conn.close()
print('New travel_agency.db created successfully!')