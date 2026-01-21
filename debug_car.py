"""
Debug script to see full car rental response.
"""
import asyncio
import json
import uuid
import httpx

async def test_car():
    query = "Rent an SUV in London, pick-up January 20, 2026, drop-off January 27, 2026"
    
    request_payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/stream",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"text": query}]
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:10105",
            json=request_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            response_text = response.text.strip()
            
            # Parse SSE format
            messages = []
            for line in response_text.split('\n'):
                if line.startswith('data: '):
                    json_str = line[6:]
                    try:
                        msg = json.loads(json_str)
                        messages.append(msg)
                    except json.JSONDecodeError:
                        continue
            
            print(f"\n{'='*80}\nFULL RESPONSE - {len(messages)} messages\n{'='*80}\n")
            
            for i, msg in enumerate(messages, 1):
                print(f"\n--- Message {i} ---")
                print(json.dumps(msg, indent=2))

asyncio.run(test_car())
