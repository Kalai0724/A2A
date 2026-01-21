"""
Test flight booking with complete information to get actual ticket results.
"""
import asyncio
import json
import uuid
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

async def book_flight_with_details():
    """Test flight booking with all required details."""
    
    console.print("\n[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]   Flight Booking Test - Complete Query   [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════[/bold cyan]\n")
    
    # Detailed query with all information
    query = """I need to book a round-trip flight:
- From: San Francisco (SFO)
- To: London (LHR)
- Departure: January 20, 2026
- Return: January 27, 2026
- Cabin class: Economy
- Passengers: 1 adult

Please show me all available flights."""
    
    console.print(Panel(query, title="[bold]Query[/bold]", border_style="cyan"))
    
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
    
    console.print("\n[yellow]⏳ Sending request to Air Ticketing Agent...[/yellow]\n")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:10103",
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
                
                console.print(f"[green]✓ Received {len(messages)} message(s)[/green]\n")
                
                # Extract and display flight information
                flights_found = False
                for msg in messages:
                    if 'result' in msg:
                        result = msg['result']
                        
                        # Check for artifacts with flight data
                        if result.get('kind') == 'artifact-update':
                            artifact = result.get('artifact', {})
                            console.print(Panel.fit(
                                "[bold green]Flight Search Results[/bold green]",
                                border_style="green"
                            ))
                            
                            for part in artifact.get('parts', []):
                                if 'text' in part:
                                    console.print(f"\n{part['text']}\n")
                                    flights_found = True
                                elif 'data' in part:
                                    # Structured flight data
                                    data = part['data']
                                    console.print(json.dumps(data, indent=2))
                                    flights_found = True
                        
                        # Check status messages
                        elif result.get('kind') == 'status-update':
                            status = result.get('status', {})
                            if status.get('message'):
                                msg_parts = status['message'].get('parts', [])
                                for part in msg_parts:
                                    if 'text' in part:
                                        text = part['text']
                                        if 'Processing' not in text:  # Skip processing messages
                                            console.print(f"[yellow]Agent:[/yellow] {text}")
                
                if not flights_found:
                    console.print("\n[yellow]No flight data found. Full response:[/yellow]")
                    for i, msg in enumerate(messages, 1):
                        console.print(f"\n[dim]Message {i}:[/dim]")
                        console.print(json.dumps(msg, indent=2))
                
                return True
            else:
                console.print(f"[red]✗ HTTP {response.status_code}[/red]")
                console.print(response.text)
                return False
                
    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to agent[/red]")
        console.print("[yellow]Make sure the Air Ticketing Agent is running on port 10103[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return False


async def main():
    success = await book_flight_with_details()
    
    if success:
        console.print("\n[green]✓ Test completed![/green]")
    else:
        console.print("\n[red]✗ Test failed[/red]")


if __name__ == "__main__":
    asyncio.run(main())
