"""
Unified Travel Assistant - One CLI for all travel bookings.
Handles flights, hotels, and car rentals in a single interactive session.
"""
import asyncio
import json
import sys
import uuid
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

AGENT_PORTS = {
    "flight": 10103,
    "hotel": 10104,
    "car": 10105
}

# Track active conversations
conversation_state = {
    "active_agent": None,
    "agent_port": None,
    "context_id": None,
    "waiting_for_answer": False
}

async def send_to_agent(port: int, query: str, context_id: str = None):
    """Send query to specific agent and return results."""
    
    message_params = {
        "messageId": str(uuid.uuid4()),
        "role": "user",
        "parts": [{"text": query}]
    }
    
    # Add context if continuing conversation
    if context_id:
        message_params["contextId"] = context_id
    
    request_payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/stream",
        "params": {
            "message": message_params
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"http://localhost:{port}",
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
                
                # Extract context ID from response
                for msg in messages:
                    if 'result' in msg:
                        result = msg['result']
                        if 'contextId' in result:
                            return messages, result['contextId']
                
                return messages, None
            else:
                return None, None
                
    except httpx.ConnectError:
        return None, None
    except Exception:
        return None, None


def detect_query_type(query: str):
    """Detect what type of booking the user wants."""
    query_lower = query.lower()
    
    # Flight keywords
    if any(word in query_lower for word in ['flight', 'fly', 'airline', 'departing', 'ticket', 'airfare']):
        return 'flight'
    
    # Hotel keywords
    if any(word in query_lower for word in ['hotel', 'accommodation', 'stay', 'room', 'check-in', 'airbnb', 'lodging']):
        return 'hotel'
    
    # Car keywords
    if any(word in query_lower for word in ['car', 'rental', 'rent', 'vehicle', 'suv', 'sedan', 'truck', 'pick-up', 'drop-off']):
        return 'car'
    
    return None


def display_flight_results(messages):
    """Display flight booking results."""
    needs_input = False
    
    for msg in messages:
        if 'result' in msg:
            result = msg['result']
            
            if result.get('kind') == 'artifact-update':
                artifact = result.get('artifact', {})
                
                for part in artifact.get('parts', []):
                    if 'data' in part:
                        flight_data = part['data']
                        
                        console.print(Panel.fit(
                            "[bold green]✈️  Flight Booking Complete![/bold green]",
                            border_style="green"
                        ))
                        
                        if 'onward' in flight_data:
                            onward = flight_data['onward']
                            console.print(f"\n[bold cyan]Outbound:[/bold cyan]")
                            console.print(f"  {onward['airline']} {onward['flight_number']}")
                            console.print(f"  From {onward['airport']} on {onward['date']}")
                            console.print(f"  Class: {onward['travel_class']}")
                            console.print(f"  Price: ${onward['cost']}")
                        
                        if 'return' in flight_data:
                            ret = flight_data['return']
                            console.print(f"\n[bold cyan]Return:[/bold cyan]")
                            console.print(f"  {ret['airline']} {ret['flight_number']}")
                            console.print(f"  From {ret['airport']} on {ret['date']}")
                            console.print(f"  Class: {ret['travel_class']}")
                            console.print(f"  Price: ${ret['cost']}")
                        
                        if 'total_price' in flight_data:
                            console.print(f"\n[bold green]Total: ${flight_data['total_price']}[/bold green]")
            
            elif result.get('kind') == 'status-update':
                status = result.get('status', {})
                if status.get('state') == 'input-required' and status.get('message'):
                    needs_input = True
                    msg_parts = status['message'].get('parts', [])
                    for part in msg_parts:
                        if 'text' in part:
                            console.print(f"\n[yellow]Agent:[/yellow] {part['text']}")
    
    return needs_input


def display_hotel_results(messages):
    """Display hotel booking results."""
    needs_input = False
    
    for msg in messages:
        if 'result' in msg:
            result = msg['result']
            
            if result.get('kind') == 'artifact-update':
                artifact = result.get('artifact', {})
                
                for part in artifact.get('parts', []):
                    if 'data' in part:
                        hotel_data = part['data']
                        
                        console.print(Panel.fit(
                            "[bold green]🏨 Hotel Booking Complete![/bold green]",
                            border_style="green"
                        ))
                        
                        if 'name' in hotel_data:
                            console.print(f"\n[bold cyan]Hotel:[/bold cyan] {hotel_data['name']}")
                        
                        if 'city' in hotel_data:
                            console.print(f"[bold cyan]Location:[/bold cyan] {hotel_data['city']}")
                        
                        if 'hotel_type' in hotel_data:
                            console.print(f"[bold cyan]Property:[/bold cyan] {hotel_data['hotel_type']}")
                        
                        if 'room_type' in hotel_data:
                            console.print(f"[bold cyan]Room:[/bold cyan] {hotel_data['room_type']}")
                        
                        if 'check_in_time' in hotel_data:
                            console.print(f"[bold cyan]Check-in:[/bold cyan] {hotel_data['check_in_time']}")
                        
                        if 'check_out_time' in hotel_data:
                            console.print(f"[bold cyan]Check-out:[/bold cyan] {hotel_data['check_out_time']}")
                        
                        if 'price_per_night' in hotel_data:
                            console.print(f"[bold cyan]Per Night:[/bold cyan] ${hotel_data['price_per_night']}")
                        
                        if 'total_rate_usd' in hotel_data:
                            console.print(f"\n[bold green]Total: ${hotel_data['total_rate_usd']}[/bold green]")
            
            elif result.get('kind') == 'status-update':
                status = result.get('status', {})
                if status.get('state') == 'input-required' and status.get('message'):
                    needs_input = True
                    msg_parts = status['message'].get('parts', [])
                    for part in msg_parts:
                        if 'text' in part:
                            console.print(f"\n[yellow]Agent:[/yellow] {part['text']}")
    
    return needs_input


def display_car_results(messages):
    """Display car rental results."""
    needs_input = False
    
    for msg in messages:
        if 'result' in msg:
            result = msg['result']
            
            if result.get('kind') == 'artifact-update':
                artifact = result.get('artifact', {})
                
                for part in artifact.get('parts', []):
                    if 'data' in part:
                        car_data = part['data']
                        
                        console.print(Panel.fit(
                            "[bold green]🚗 Car Rental Complete![/bold green]",
                            border_style="green"
                        ))
                        
                        if 'car_type' in car_data:
                            console.print(f"\n[bold cyan]Vehicle:[/bold cyan] {car_data['car_type']}")
                        
                        if 'provider' in car_data:
                            console.print(f"[bold cyan]Company:[/bold cyan] {car_data['provider']}")
                        
                        if 'city' in car_data:
                            console.print(f"[bold cyan]Location:[/bold cyan] {car_data['city']}")
                        
                        if 'pickup_date' in car_data:
                            console.print(f"[bold cyan]Pick-up:[/bold cyan] {car_data['pickup_date']}")
                        
                        if 'return_date' in car_data:
                            console.print(f"[bold cyan]Drop-off:[/bold cyan] {car_data['return_date']}")
                        
                        if 'price' in car_data:
                            console.print(f"\n[bold green]Total: ${car_data['price']}[/bold green]")
            
            elif result.get('kind') == 'status-update':
                status = result.get('status', {})
                if status.get('state') == 'input-required' and status.get('message'):
                    needs_input = True
                    msg_parts = status['message'].get('parts', [])
                    for part in msg_parts:
                        if 'text' in part:
                            console.print(f"\n[yellow]Agent:[/yellow] {part['text']}")
    
    return needs_input


async def process_query(query: str):
    """Process a travel query."""
    global conversation_state
    
    # Check if we're continuing a conversation
    if conversation_state["waiting_for_answer"]:
        # Send response to the active agent with context
        port = conversation_state["agent_port"]
        context_id = conversation_state["context_id"]
        query_type = conversation_state["active_agent"]
        
        type_icons = {
            'flight': '✈️',
            'hotel': '🏨',
            'car': '🚗'
        }
        console.print(f"[dim]{type_icons[query_type]} Continuing {query_type} booking...[/dim]\n")
    else:
        # Detect query type for new conversation
        query_type = detect_query_type(query)
        
        if not query_type:
            console.print("\n[yellow]I couldn't determine what you're looking for.[/yellow]")
            console.print("[dim]Try mentioning: flight, hotel, or car rental[/dim]")
            console.print("[dim]Or type 'help' for examples[/dim]")
            return
        
        # Show what we detected
        type_icons = {
            'flight': '✈️  Flight',
            'hotel': '🏨 Hotel',
            'car': '🚗 Car Rental'
        }
        console.print(f"\n[cyan]Detected:[/cyan] {type_icons[query_type]}")
        console.print("[dim]Processing your request...[/dim]\n")
        
        port = AGENT_PORTS[query_type]
        context_id = None
    
    # Send to agent
    result = await send_to_agent(port, query, context_id)
    
    if not result or result[0] is None:
        console.print("[red]✗ Could not connect to agent[/red]")
        console.print("[yellow]Make sure all agents are running: .\\start_all.ps1[/yellow]")
        conversation_state = {"active_agent": None, "agent_port": None, "context_id": None, "waiting_for_answer": False}
        return
    
    messages, new_context_id = result
    
    # Display results and check if agent needs more input
    needs_input = False
    if query_type == 'flight':
        needs_input = display_flight_results(messages)
    elif query_type == 'hotel':
        needs_input = display_hotel_results(messages)
    elif query_type == 'car':
        needs_input = display_car_results(messages)
    
    # Update conversation state
    if needs_input and new_context_id:
        conversation_state = {
            "active_agent": query_type,
            "agent_port": port,
            "context_id": new_context_id,
            "waiting_for_answer": True
        }
    else:
        # Conversation complete, reset state
        conversation_state = {
            "active_agent": None,
            "agent_port": None,
            "context_id": None,
            "waiting_for_answer": False
        }


async def main():
    """Main interactive loop."""
    
    console.print("\n[bold magenta]╔════════════════════════════════════════════════╗[/bold magenta]")
    console.print("[bold magenta]║   🌍 Unified Travel Assistant 🌍              ║[/bold magenta]")
    console.print("[bold magenta]╚════════════════════════════════════════════════╝[/bold magenta]\n")
    
    console.print("[bold cyan]I can help you book:[/bold cyan]")
    console.print("  ✈️  Flights")
    console.print("  🏨 Hotels")
    console.print("  🚗 Car Rentals\n")
    
    console.print("[dim]Just describe what you need in natural language.[/dim]")
    console.print("[dim]Type 'help' to see examples, or 'quit' to exit.[/dim]\n")
    
    while True:
        try:
            # Show context indicator if in conversation
            if conversation_state["waiting_for_answer"]:
                type_icons = {
                    'flight': '✈️',
                    'hotel': '🏨',
                    'car': '🚗'
                }
                icon = type_icons.get(conversation_state["active_agent"], "💬")
                query = Prompt.ask(f"\n[bold green]{icon} Answer[/bold green]")
            else:
                query = Prompt.ask("\n[bold green]You[/bold green]")
            
            if query.lower() in ['quit', 'exit', 'q']:
                console.print("\n[yellow]👋 Thank you for using Travel Assistant![/yellow]\n")
                break
            
            if query.lower() in ['help', 'examples', '?']:
                console.print("\n[bold cyan]Example Queries:[/bold cyan]")
                console.print("\n[yellow]Flights:[/yellow]")
                console.print("  • Book economy flight from San Francisco to London, Jan 20-27, 2026, 1 adult")
                console.print("  • Business class flight from New York to Paris, departing Feb 1, returning Feb 8")
                
                console.print("\n[yellow]Hotels:[/yellow]")
                console.print("  • Find hotels in London. Check-in: Jan 20, 2026. Check-out: Jan 27, 2026. Property type: Hotel. Room type: Suite. Guests: 1")
                console.print("  • Book AirBnB in Paris, Feb 1-8, 2026, Standard room, 2 guests")
                
                console.print("\n[yellow]Car Rentals:[/yellow]")
                console.print("  • Rent an SUV in London, pick-up Jan 20, 2026, drop-off Jan 27, 2026")
                console.print("  • Need a sedan in Paris from Feb 1 to Feb 8, 2026\n")
                continue
            
            if query.lower() == 'reset':
                conversation_state = {"active_agent": None, "agent_port": None, "context_id": None, "waiting_for_answer": False}
                console.print("[yellow]Conversation reset. Start a new booking.[/yellow]")
                continue
            
            if not query.strip():
                continue
            
            await process_query(query)
            
        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Goodbye![/yellow]\n")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            conversation_state = {"active_agent": None, "agent_port": None, "context_id": None, "waiting_for_answer": False}
            continue


if __name__ == "__main__":
    asyncio.run(main())
