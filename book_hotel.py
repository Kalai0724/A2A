"""
Quick hotel booking script - use from command line.
Usage: uv run book_hotel.py "your query here"
"""
import asyncio
import json
import sys
import uuid
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

async def book_hotel(query: str):
    """Send hotel booking request and display results."""
    
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
    
    console.print(Panel(query, title="[bold]Your Request[/bold]", border_style="cyan"))
    console.print("\n[yellow]⏳ Searching for hotels...[/yellow]\n")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:10104",
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
                
                # Extract results
                found_data = False
                for msg in messages:
                    if 'result' in msg:
                        result = msg['result']
                        
                        # Hotel data in artifacts
                        if result.get('kind') == 'artifact-update':
                            artifact = result.get('artifact', {})
                            
                            for part in artifact.get('parts', []):
                                if 'data' in part:
                                    hotel_data = part['data']
                                    found_data = True
                                    
                                    # Display hotel details
                                    console.print(Panel.fit(
                                        "[bold green]✓ Hotel Booking Complete![/bold green]",
                                        border_style="green"
                                    ))
                                    
                                    if 'name' in hotel_data:
                                        console.print(f"\n[bold cyan]Hotel:[/bold cyan] {hotel_data['name']}")
                                    elif 'hotel_name' in hotel_data:
                                        console.print(f"\n[bold cyan]Hotel:[/bold cyan] {hotel_data['hotel_name']}")
                                    
                                    if 'city' in hotel_data:
                                        console.print(f"[bold cyan]Location:[/bold cyan] {hotel_data['city']}")
                                    elif 'location' in hotel_data:
                                        console.print(f"[bold cyan]Location:[/bold cyan] {hotel_data['location']}")
                                    
                                    if 'hotel_type' in hotel_data:
                                        console.print(f"[bold cyan]Property Type:[/bold cyan] {hotel_data['hotel_type']}")
                                    elif 'property_type' in hotel_data:
                                        console.print(f"[bold cyan]Property Type:[/bold cyan] {hotel_data['property_type']}")
                                    
                                    if 'room_type' in hotel_data:
                                        console.print(f"[bold cyan]Room Type:[/bold cyan] {hotel_data['room_type']}")
                                    
                                    if 'check_in_time' in hotel_data:
                                        console.print(f"[bold cyan]Check-in Time:[/bold cyan] {hotel_data['check_in_time']}")
                                    elif 'check_in_date' in hotel_data:
                                        console.print(f"[bold cyan]Check-in:[/bold cyan] {hotel_data['check_in_date']}")
                                    
                                    if 'check_out_time' in hotel_data:
                                        console.print(f"[bold cyan]Check-out Time:[/bold cyan] {hotel_data['check_out_time']}")
                                    elif 'check_out_date' in hotel_data:
                                        console.print(f"[bold cyan]Check-out:[/bold cyan] {hotel_data['check_out_date']}")
                                    
                                    if 'price_per_night' in hotel_data:
                                        console.print(f"[bold cyan]Nightly Rate:[/bold cyan] ${hotel_data['price_per_night']}")
                                    elif 'nightly_rate' in hotel_data:
                                        console.print(f"[bold cyan]Nightly Rate:[/bold cyan] ${hotel_data['nightly_rate']}")
                                    
                                    if 'total_rate_usd' in hotel_data:
                                        console.print(f"\n[bold green]Total Price: ${hotel_data['total_rate_usd']}[/bold green]")
                                    elif 'price' in hotel_data:
                                        console.print(f"\n[bold green]Total Price: ${hotel_data['price']}[/bold green]")
                                    elif 'total_cost' in hotel_data:
                                        console.print(f"\n[bold green]Total Price: ${hotel_data['total_cost']}[/bold green]")
                                    
                                    if 'description' in hotel_data:
                                        console.print(f"[dim]{hotel_data['description']}[/dim]")
                                
                                elif 'text' in part:
                                    text = part['text']
                                    if text and 'Processing' not in text:
                                        console.print(f"\n[cyan]Agent:[/cyan] {text}")
                                        found_data = True
                        
                        # Status messages
                        elif result.get('kind') == 'status-update':
                            status = result.get('status', {})
                            if status.get('state') == 'input-required' and status.get('message'):
                                msg_parts = status['message'].get('parts', [])
                                for part in msg_parts:
                                    if 'text' in part:
                                        console.print(f"\n[yellow]📋 Agent Response:[/yellow]")
                                        console.print(part['text'])
                                        found_data = True
                
                if found_data:
                    return True
                else:
                    console.print("[yellow]No hotel information found in response[/yellow]")
                    return False
                
            else:
                console.print(f"[red]✗ HTTP {response.status_code}[/red]")
                return False
                
    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to Hotel Booking Agent[/red]")
        console.print("[yellow]Make sure agents are running: .\\start_all.ps1[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


async def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Default query with all details
        query = """Book a hotel in London, check-in January 20, 2026, check-out January 27, 2026, 
Hotel type, 2 guests."""
    
    console.print("\n[bold magenta]═══════════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]        Hotel Booking Assistant         [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════════[/bold magenta]\n")
    
    await book_hotel(query)


if __name__ == "__main__":
    asyncio.run(main())
