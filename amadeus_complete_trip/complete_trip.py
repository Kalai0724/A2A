import asyncio
import httpx
import json
import uuid
import sys

AGENTS = {
    "flight": 10103,
    "hotel": 10104,
    "weather": 10106

}

async def call_agent(port: int, query: str):
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"text": query}]
            }
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(f"http://localhost:{port}", json=payload)
        return r.json()

def extract_data(resp):
    try:
        return resp["result"]["artifact"]["parts"][0]["data"]
    except:
        return []

async def main():
    if len(sys.argv) < 2:
        print('Usage: uv run complete_trip.py "your query here"')
        return

    query = " ".join(sys.argv[1:])

    flight_resp = await call_agent(AGENTS["flight"], query)
    hotel_resp = await call_agent(AGENTS["hotel"], query)
    weather_resp = await call_agent(AGENTS["weather"], query)

    flights = extract_data(flight_resp)
    hotels = extract_data(hotel_resp)
    weather = extract_data(weather_resp)

    print("\n✈️ Flights:\n", json.dumps(flights, indent=2))
    print("\n🏨 Hotels:\n", json.dumps(hotels, indent=2))
    print("\n🌦️ Weather:\n", json.dumps(weather, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
