"""
Quick car rental booking script - use from command line.
Usage: uv run book_car.py "your query here"
"""
import asyncio
import json
import sys
import uuid
import httpx
from rich.console import Console
from rich.panel import Panel

console = Console()

async def book_car(query: str):
    """Send car rental booking request and display results."""
    
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
    console.print("\n[yellow]⏳ Searching for rental cars...[/yellow]\n")
    
    try:
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
                
                # Extract results
                found_data = False
                for msg in messages:
                    if 'result' in msg:
                        result = msg['result']
                        
                        # Car rental data in artifacts
                        if result.get('kind') == 'artifact-update':
                            artifact = result.get('artifact', {})
                            
                            for part in artifact.get('parts', []):
                                if 'data' in part:
                                    car_data = part['data']
                                    found_data = True
                                    
                                    # Display car rental details
                                    console.print(Panel.fit(
                                        "[bold green]✓ Booking Complete![/bold green]",
                                        border_style="green"
                                    ))
                                    
                                    if 'car_type' in car_data:
                                        console.print(f"\n[bold cyan]Vehicle:[/bold cyan] {car_data['car_type']}")
                                    
                                    if 'provider' in car_data:
                                        console.print(f"[bold cyan]Rental Company:[/bold cyan] {car_data['provider']}")
                                    elif 'rental_company' in car_data:
                                        console.print(f"[bold cyan]Rental Company:[/bold cyan] {car_data['rental_company']}")
                                    
                                    if 'city' in car_data:
                                        console.print(f"[bold cyan]Location:[/bold cyan] {car_data['city']}")
                                    elif 'location' in car_data:
                                        console.print(f"[bold cyan]Location:[/bold cyan] {car_data['location']}")
                                    
                                    if 'pickup_date' in car_data:
                                        console.print(f"[bold cyan]Pick-up:[/bold cyan] {car_data['pickup_date']}")
                                    
                                    if 'return_date' in car_data:
                                        console.print(f"[bold cyan]Drop-off:[/bold cyan] {car_data['return_date']}")
                                    elif 'dropoff_date' in car_data:
                                        console.print(f"[bold cyan]Drop-off:[/bold cyan] {car_data['dropoff_date']}")
                                    
                                    if 'daily_rate' in car_data:
                                        console.print(f"[bold cyan]Daily Rate:[/bold cyan] ${car_data['daily_rate']}")
                                    
                                    if 'price' in car_data:
                                        console.print(f"\n[bold green]Total Price: ${car_data['price']}[/bold green]")
                                    elif 'total_cost' in car_data:
                                        console.print(f"\n[bold green]Total Price: ${car_data['total_cost']}[/bold green]")
                                    
                                    if 'description' in car_data:
                                        console.print(f"[dim]{car_data['description']}[/dim]")
                                
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
                    console.print("[yellow]No car rental information found in response[/yellow]")
                    return False
                
            else:
                console.print(f"[red]✗ HTTP {response.status_code}[/red]")
                return False
                
    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to Car Rental Agent[/red]")
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
        query = """Rent a sedan in London, pick-up January 20, 2026, drop-off January 27, 2026."""
    
    console.print("\n[bold magenta]═══════════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]      Car Rental Booking Assistant       [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════════[/bold magenta]\n")
    
    await book_car(query)


if __name__ == "__main__":
    asyncio.run(main())

