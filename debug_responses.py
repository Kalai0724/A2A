"""Debug version to see what agents are returning"""
import asyncio
import json
import uuid
import httpx

async def test_hotel():
    request_payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/stream",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"text": "Find hotels in Paris. Check-in: February 1, 2026. Check-out: February 8, 2026. Property type: AIRBNB. Room type: STANDARD. Number of guests: 2"}]
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:10104",
            json=request_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print("=== HOTEL RESPONSE ===")
        print(response.text)

async def test_car():
    request_payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/stream",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"text": "Rent a SEDAN in Paris, pick-up February 1, 2026, drop-off February 8, 2026"}]
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:10105",
            json=request_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print("\n=== CAR RESPONSE ===")
        print(response.text)

asyncio.run(test_hotel())
asyncio.run(test_car())
