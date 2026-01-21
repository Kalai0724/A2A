import os
import requests
from datetime import datetime, timedelta

API_KEY = os.getenv("FLIGHT_API_KEY")
BASE_URL = "https://api.flightapi.io/onewaytrip"

def validate_date(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    if date > datetime.now() + timedelta(days=60):
        raise ValueError("FlightAPI free plan supports only near future dates (≤60 days)")
    return date_str

def search_oneway(origin, destination, depart_date, adults=1):
    validate_date(depart_date)

    url = f"{BASE_URL}/{API_KEY}/{origin}/{destination}/{depart_date}/{adults}/0/0/economy"

    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            return {"error": f"FlightAPI error {r.status_code}"}
        return r.json()
    except requests.exceptions.Timeout:
        return {"error": "FlightAPI timeout (provider issue)"}
