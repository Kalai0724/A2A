from flight_agent import search_oneway

print("✈️ Flight Agent (FlightAPI.io)")

trip = input("Trip type (oneway/roundtrip): ").lower()

if trip == "roundtrip":
    print("⚠️ Round-trip NOT supported on FlightAPI free plan.")
    exit()

origin = input("From (IATA): ").upper()
destination = input("To (IATA): ").upper()
date = input("Departure date (YYYY-MM-DD): ")
adults = int(input("Adults (default 1): ") or 1)

print("\nSearching flights...\n")
result = search_oneway(origin, destination, date, adults)

if "error" in result:
    print("❌", result["error"])
else:
    print("✅ Flights found")
    print(result)
