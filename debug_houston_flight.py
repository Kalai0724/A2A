"""Debug Houston to Paris flight"""
import asyncio
import json
import uuid
import httpx

async def test_flight():
    request = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/stream",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"text": "Book business flight from Houston to Paris, departing July 5, 2026, returning July 19, 2026, 1 adult"}]
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post("http://localhost:10103", json=request)
        
        print("=== FULL FLIGHT RESPONSE ===\n")
        
        for line in response.text.split('\n'):
            if line.startswith('data: '):
                try:
                    msg = json.loads(line[6:])
                    if 'result' in msg:
                        result = msg['result']
                        if result.get('kind') == 'artifact-update':
                            print(json.dumps(result.get('artifact', {}), indent=2))
                        elif result.get('kind') == 'status-update':
                            status = result.get('status', {})
                            if 'message' in status:
                                print(f"Status: {status.get('state')}")
                                for part in status['message'].get('parts', []):
                                    if 'text' in part:
                                        print(f"  Agent: {part['text']}")
                except:
                    pass

asyncio.run(test_flight())
