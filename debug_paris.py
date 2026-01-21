"""Quick debug to see Paris hotel/car responses"""
import asyncio
import json
import uuid
import httpx

async def test():
    # Test Paris hotel
    hotel_req = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/stream",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"text": "Book a hotel in Paris. Check-in date: July 5, 2026. Check-out date: July 19, 2026. Hotel type: HOTEL. Room type: DELUXE. Number of guests: 1. Confirm booking."}]
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post("http://localhost:10104", json=hotel_req)
        print("=== PARIS HOTEL ===")
        for line in r.text.split('\n'):
            if 'input-required' in line or 'artifact-update' in line:
                print(line)
        
        # Test Paris car
        car_req = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "message/stream",
            "params": {
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "user",
                    "parts": [{"text": "I need to rent a SEDAN in Paris. Pickup date is July 5, 2026. Return date is July 19, 2026. Please confirm the booking."}]
                }
            }
        }
        
        r = await client.post("http://localhost:10105", json=car_req)
        print("\n=== PARIS CAR ===")
        for line in r.text.split('\n'):
            if 'input-required' in line or 'artifact-update' in line:
                print(line)

asyncio.run(test())
