import asyncio
import os
import json
import logging
from dotenv import load_dotenv
import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("flight_bot.log"),
        logging.StreamHandler()
    ]
)

load_dotenv()
API_KEY = os.getenv("FLIGHT_API_KEY")

async def get_flights(origin, destination, departure_date, return_date, adults=1, children=0, infants=0, cabin="economy"):
    url = f"https://api.flightapi.io/oneway/{API_KEY}/{origin}/{destination}/{departure_date}/{return_date}/{adults}/{children}/{infants}/{cabin}"
    logging.info(f"Requesting URL: {url}")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            logging.info(f"Response status: {response.status_code}")
            logging.info(f"Response text: {response.text[:500]}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        logging.error(f"Exception during API call: {e}")
        return {"error": str(e)}

def pretty_print_flights(data):
    if "error" in data:
        logging.error(f"Bot: Sorry, {data['error']} from the flight API.")
        print(f"Bot: Sorry, {data['error']} from the flight API.")
        return
    if not data.get("trips"):
        logging.info("Bot: No flights found for your search.")
        print("Bot: No flights found for your search.")
        return
    logging.info("Bot: Here are some flight options:")
    print("Bot: Here are some flight options:")
    for trip in data["trips"]:
        for slice_ in trip.get("slices", []):
            for segment in slice_.get("segments", []):
                logging.info(f"  Airline: {segment.get('airlineName', 'N/A')}")
                print(f"  Airline: {segment.get('airlineName', 'N/A')}")
                logging.info(f"  Flight: {segment.get('flightNumber', 'N/A')}")
                print(f"  Flight: {segment.get('flightNumber', 'N/A')}")
                logging.info(f"  From: {segment.get('origin', 'N/A')} To: {segment.get('destination', 'N/A')}")
                print(f"  From: {segment.get('origin', 'N/A')} To: {segment.get('destination', 'N/A')}")
                logging.info(f"  Departure: {segment.get('departureDateTime', 'N/A')}")
                print(f"  Departure: {segment.get('departureDateTime', 'N/A')}")
                logging.info(f"  Arrival: {segment.get('arrivalDateTime', 'N/A')}")
                print(f"  Arrival: {segment.get('arrivalDateTime', 'N/A')}")
        price = trip.get("price", {})
        logging.info(f"  Price: {price.get('total', 'N/A')} {price.get('currency', '')}")
        print(f"  Price: {price.get('total', 'N/A')} {price.get('currency', '')}")
        logging.info("-")
        print("-")

async def main():
    print("Bot: Welcome! I can help you book a flight.")
    origin = input("Bot: Enter origin airport code (e.g., JFK): ").strip().upper()
    destination = input("Bot: Enter destination airport code (e.g., LAX): ").strip().upper()
    departure_date = input("Bot: Enter departure date (YYYY-MM-DD): ").strip()
    return_date = input("Bot: Enter return date (YYYY-MM-DD): ").strip()
    adults = input("Bot: Number of adults (default 1): ").strip() or "1"
    children = input("Bot: Number of children (default 0): ").strip() or "0"
    infants = input("Bot: Number of infants (default 0): ").strip() or "0"
    cabin = input("Bot: Cabin class (economy/business/first, default economy): ").strip() or "economy"
    print("Bot: Searching for flights...")
    data = await get_flights(origin, destination, departure_date, return_date, adults, children, infants, cabin)
    pretty_print_flights(data)

if __name__ == "__main__":
    asyncio.run(main())