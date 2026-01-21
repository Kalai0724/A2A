"""
Interactive booking assistant - have a conversation with travel agents.
Usage: uv run interactive_booking.py [flight|hotel|car]
"""
import asyncio
import json
import sys
import uuid
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

AGENT_PORTS = {
    "flight": 10103,
    "hotel": 10104,
    "car": 10105
}

AGENT_NAMES = {
    "flight": "Air Ticketing Agent",
    "hotel": "Hotel Booking Agent",
    "car": "Car Rental Agent"
}

async def send_message(port: int, query: str, context_id: str):
    """Send a message to an agent and get response."""
    
    request_payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/stream",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"text": query}]
            },
            "contextId": context_id
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
                
                return messages
            else:
                console.print(f"[red]✗ HTTP {response.status_code}[/red]")
                return None
                
    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to agent on port {port}[/red]")
        console.print("[yellow]Make sure agents are running: .\\start_all.ps1[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return None


def display_response(messages, agent_type):
    """Display agent response and check if booking is complete."""
    
    booking_complete = False
    needs_input = False
    agent_question = None
    booking_data = None
    
    for msg in messages:
        if 'result' in msg:
            result = msg['result']
            
            # Check for booking data in artifacts
            if result.get('kind') == 'artifact-update':
                artifact = result.get('artifact', {})
                
                for part in artifact.get('parts', []):
                    if 'data' in part:
                        booking_data = part['data']
                        
                        # Check if booking is complete
                        if booking_data.get('status') in ['completed', 'BOOKING_COMPLETE']:
                            booking_complete = True
                            
                            console.print(Panel.fit(
                                "[bold green]✓ Booking Complete![/bold green]",
                                border_style="green"
                            ))
                            
                            # Display booking details based on agent type
                            if agent_type == "flight":
                                if 'onward' in booking_data:
                                    onward = booking_data['onward']
                                    console.print(f"\n[bold cyan]Outbound:[/bold cyan] {onward['airline']} {onward['flight_number']}")
                                    console.print(f"  {onward['airport']} on {onward['date']}, {onward['travel_class']}")
                                    console.print(f"  ${onward['cost']}")
                                
                                if 'return' in booking_data:
                                    ret = booking_data['return']
                                    console.print(f"\n[bold cyan]Return:[/bold cyan] {ret['airline']} {ret['flight_number']}")
                                    console.print(f"  {ret['airport']} on {ret['date']}, {ret['travel_class']}")
                                    console.print(f"  ${ret['cost']}")
                                
                                if 'total_price' in booking_data:
                                    console.print(f"\n[bold green]Total: ${booking_data['total_price']}[/bold green]")
                            
                            elif agent_type == "hotel":
                                if 'hotel_name' in booking_data:
                                    console.print(f"\n[bold cyan]Hotel:[/bold cyan] {booking_data['hotel_name']}")
                                if 'location' in booking_data:
                                    console.print(f"[bold cyan]Location:[/bold cyan] {booking_data['location']}")
                                if 'total_cost' in booking_data:
                                    console.print(f"\n[bold green]Total: ${booking_data['total_cost']}[/bold green]")
                            
                            elif agent_type == "car":
                                if 'car_type' in booking_data:
                                    console.print(f"\n[bold cyan]Vehicle:[/bold cyan] {booking_data['car_type']}")
                                if 'rental_company' in booking_data:
                                    console.print(f"[bold cyan]Company:[/bold cyan] {booking_data['rental_company']}")
                                if 'total_cost' in booking_data:
                                    console.print(f"\n[bold green]Total: ${booking_data['total_cost']}[/bold green]")
                    
                    elif 'text' in part:
                        text = part['text']
                        if text and 'Processing' not in text:
                            console.print(f"\n[yellow]Agent:[/yellow] {text}")
            
            # Check status messages
            elif result.get('kind') == 'status-update':
                status = result.get('status', {})
                
                # Check if completed
                if status.get('state') == 'completed' and status.get('final'):
                    if not booking_data:  # Only mark complete if we haven't already found booking data
                        booking_complete = True
                
                # Check if input required
                if status.get('state') == 'input-required' and status.get('message'):
                    needs_input = True
                    msg_parts = status['message'].get('parts', [])
                    for part in msg_parts:
                        if 'text' in part:
                            agent_question = part['text']
                            console.print(f"\n[yellow]Agent:[/yellow] {part['text']}")
    
    return booking_complete, needs_input, agent_question


async def interactive_booking(agent_type):
    """Run an interactive booking conversation."""
    
    if agent_type not in AGENT_PORTS:
        console.print(f"[red]Unknown agent type: {agent_type}[/red]")
        console.print("[yellow]Use: flight, hotel, or car[/yellow]")
        return
    
    port = AGENT_PORTS[agent_type]
    agent_name = AGENT_NAMES[agent_type]
    context_id = str(uuid.uuid4())
    
    console.print(f"\n[bold magenta]{'═' * 50}[/bold magenta]")
    console.print(f"[bold magenta]   Interactive {agent_name}   [/bold magenta]")
    console.print(f"[bold magenta]{'═' * 50}[/bold magenta]\n")
    
    console.print("[dim]Type your booking request or answer agent questions.[/dim]")
    console.print("[dim]Type 'quit' or 'exit' to end the conversation.[/dim]\n")
    
    # Get initial request
    user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
    
    if user_input.lower() in ['quit', 'exit']:
        return
    
    conversation_active = True
    
    while conversation_active:
        # Send message to agent
        console.print("\n[dim]⏳ Sending to agent...[/dim]")
        messages = await send_message(port, user_input, context_id)
        
        if not messages:
            break
        
        # Display response
        booking_complete, needs_input, agent_question = display_response(messages, agent_type)
        
        # Check if done
        if booking_complete:
            console.print("\n[bold green]✓ Booking session complete![/bold green]")
            break
        
        # Get next input if needed
        if needs_input or agent_question:
            console.print()
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
            
            if user_input.lower() in ['quit', 'exit']:
                console.print("\n[yellow]Ending conversation...[/yellow]")
                break
        else:
            console.print("\n[yellow]Conversation appears complete.[/yellow]")
            continue_chat = Prompt.ask("Continue conversation?", choices=["yes", "no"], default="no")
            if continue_chat == "no":
                break
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")


async def main():
    if len(sys.argv) > 1:
        agent_type = sys.argv[1].lower()
    else:
        console.print("\n[bold cyan]Choose agent type:[/bold cyan]")
        agent_type = Prompt.ask("Agent", choices=["flight", "hotel", "car"], default="flight")
    
    await interactive_booking(agent_type)


if __name__ == "__main__":
    asyncio.run(main())
