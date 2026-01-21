"""
Complete Trip Planner - Books flight, hotel, and car rental in one query.
Example: python complete_trip.py "San Francisco to London, Jan 20-27, 2026, economy flight, hotel suite, rent SUV"
"""
import asyncio
import json
import sys
import uuid
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import re

console = Console()

AGENT_PORTS = {
    "flight": 10103,
    "hotel": 10104,
    "car": 10105
}

async def send_to_agent(port: int, query: str):
    """Send query to agent and parse response."""
    
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
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"http://localhost:{port}",
                json=request_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                messages = []
                for line in response.text.strip().split('\n'):
                    if line.startswith('data: '):
                        try:
                            msg = json.loads(line[6:])
                            messages.append(msg)
                        except:
                            continue
                return messages
    except:
        return None


def parse_trip_query(query: str):
    """Parse a combined trip query into separate components."""
    query_lower = query.lower()
    
    # Extract locations
    from_match = re.search(r'from\s+([a-z\s]+?)(?:\s+to|\s*,)', query_lower)
    to_match = re.search(r'to\s+([a-z\s]+?)(?:\s*[,.]|\s+on|\s+departing|\s+jan|\s+feb|\s+mar|\s+apr|\s+may|\s+jun|\s+jul|\s+aug|\s+sep|\s+oct|\s+nov|\s+dec|\s+\d)', query_lower)
    
    origin = from_match.group(1).strip().title() if from_match else None
    destination = to_match.group(1).strip().title() if to_match else None
    
    # Extract dates
    dates = re.findall(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:\s*-\s*(\d{1,2}))?,?\s*(\d{4})', query_lower)
    start_date = None
    end_date = None
    
    if dates:
        month, day1, day2, year = dates[0]
        start_date = f"{month.title()} {day1}, {year}"
        if day2:
            end_date = f"{month.title()} {day2}, {year}"
    
    # Or try short format: Jan 20-27, 2026
    short_dates = re.findall(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})\s*-\s*(\d{1,2}),?\s*(\d{4})', query_lower)
    if short_dates:
        month_abbr, day1, day2, year = short_dates[0]
        month_map = {'jan': 'January', 'feb': 'February', 'mar': 'March', 'apr': 'April', 
                     'may': 'May', 'jun': 'June', 'jul': 'July', 'aug': 'August',
                     'sep': 'September', 'oct': 'October', 'nov': 'November', 'dec': 'December'}
        month = month_map.get(month_abbr, month_abbr)
        start_date = f"{month} {day1}, {year}"
        end_date = f"{month} {day2}, {year}"
    
    # Extract travel class
    travel_class = "ECONOMY"
    if 'business' in query_lower or 'business class' in query_lower:
        travel_class = "BUSINESS"
    elif 'first class' in query_lower or 'first' in query_lower:
        travel_class = "FIRST"
    
    # Extract adults
    adults_match = re.search(r'(\d+)\s*adults?', query_lower)
    adults = adults_match.group(1) if adults_match else "1"
    
    # Extract hotel type
    hotel_type = "HOTEL"
    if 'airbnb' in query_lower or 'air bnb' in query_lower:
        hotel_type = "AIRBNB"
    elif 'private' in query_lower:
        hotel_type = "PRIVATE_PROPERTY"
    
    # Extract room type (only use valid types from database)
    room_type = "STANDARD"
    if 'suite' in query_lower:
        room_type = "SUITE"
    elif 'single' in query_lower:
        room_type = "SINGLE"
    elif 'double' in query_lower:
        room_type = "DOUBLE"
    # Note: DELUXE is not in database, defaults to STANDARD
    
    # Extract guests
    guests_match = re.search(r'(\d+)\s*guests?', query_lower)
    guests = guests_match.group(1) if guests_match else adults
    
    # Extract car type
    car_type = None
    if 'suv' in query_lower:
        car_type = "SUV"
    elif 'sedan' in query_lower:
        car_type = "SEDAN"
    elif 'truck' in query_lower or 'pickup' in query_lower:
        car_type = "TRUCK"
    
    return {
        'origin': origin,
        'destination': destination,
        'start_date': start_date,
        'end_date': end_date,
        'travel_class': travel_class,
        'adults': adults,
        'hotel_type': hotel_type,
        'room_type': room_type,
        'guests': guests,
        'car_type': car_type
    }


def extract_flight_data(messages):
    """Extract flight booking data."""
    for msg in messages:
        if 'result' in msg:
            result = msg['result']
            if result.get('kind') == 'artifact-update':
                artifact = result.get('artifact', {})
                for part in artifact.get('parts', []):
                    if 'data' in part:
                        return part['data']
    return None


def extract_hotel_data(messages):
    """Extract hotel booking data."""
    for msg in messages:
        if 'result' in msg:
            result = msg['result']
            if result.get('kind') == 'artifact-update':
                artifact = result.get('artifact', {})
                for part in artifact.get('parts', []):
                    if 'data' in part:
                        return part['data']
    return None


def extract_car_data(messages):
    """Extract car rental data."""
    for msg in messages:
        if 'result' in msg:
            result = msg['result']
            if result.get('kind') == 'artifact-update':
                artifact = result.get('artifact', {})
                for part in artifact.get('parts', []):
                    if 'data' in part:
                        return part['data']
    return None


async def book_complete_trip(trip_details):
    """Book all three components of a trip."""
    
    console.print("\n[bold cyan]🌍 Planning Your Complete Trip...[/bold cyan]\n")
    
    results = {
        'flight': None,
        'hotel': None,
        'car': None
    }
    
    # Book Flight
    if trip_details['origin'] and trip_details['destination'] and trip_details['start_date']:
        console.print("[yellow]✈️  Booking flights...[/yellow]")
        
        flight_query = f"Book {trip_details['travel_class'].lower()} flight from {trip_details['origin']} to {trip_details['destination']}, "
        flight_query += f"departing {trip_details['start_date']}, "
        if trip_details['end_date']:
            flight_query += f"returning {trip_details['end_date']}, "
        flight_query += f"{trip_details['adults']} adult"
        
        flight_messages = await send_to_agent(AGENT_PORTS['flight'], flight_query)
        if flight_messages:
            results['flight'] = extract_flight_data(flight_messages)
            if results['flight']:
                console.print("[green]✓ Flight booked[/green]\n")
            else:
                # Check if agent asked a question
                for msg in flight_messages:
                    if 'result' in msg and msg['result'].get('kind') == 'artifact-update':
                        artifact = msg['result'].get('artifact', {})
                        for part in artifact.get('parts', []):
                            if 'text' in part and 'input_required' in part.get('text', '').lower():
                                console.print(f"[yellow]⚠ Flight: Agent needs clarification[/yellow]\n")
                                break
                if not results['flight']:
                    console.print("[yellow]⚠ Flight response incomplete[/yellow]\n")
        else:
            console.print("[red]✗ Flight booking failed[/red]\n")
    
    # Book Hotel
    if trip_details['destination'] and trip_details['start_date'] and trip_details['end_date']:
        console.print("[yellow]🏨 Booking hotel...[/yellow]")
        
        # Use HOTEL type to avoid agent asking follow-up questions about unavailable AIRBNB
        hotel_query = f"Book a hotel in {trip_details['destination']}. "
        hotel_query += f"Check-in date: {trip_details['start_date']}. "
        hotel_query += f"Check-out date: {trip_details['end_date']}. "
        hotel_query += f"Hotel type: HOTEL. "
        hotel_query += f"Room type: {trip_details['room_type']}. "
        hotel_query += f"Number of guests: {trip_details['guests']}. "
        hotel_query += f"Confirm booking."
        
        hotel_messages = await send_to_agent(AGENT_PORTS['hotel'], hotel_query)
        if hotel_messages:
            results['hotel'] = extract_hotel_data(hotel_messages)
            if results['hotel']:
                console.print("[green]✓ Hotel booked[/green]\n")
            else:
                # Check what the agent said
                for msg in hotel_messages:
                    if 'result' in msg and msg['result'].get('kind') == 'artifact-update':
                        artifact = msg['result'].get('artifact', {})
                        for part in artifact.get('parts', []):
                            if 'text' in part:
                                text = part.get('text', '')
                                if 'not supported' in text.lower() or 'choose from' in text.lower():
                                    console.print(f"[yellow]⚠ Hotel: Room type not available[/yellow]\n")
                                    break
                                elif 'input_required' in text.lower():
                                    console.print(f"[yellow]⚠ Hotel: Agent needs clarification[/yellow]\n")
                                    break
                if not results['hotel']:
                    console.print("[yellow]⚠ Hotel response incomplete[/yellow]\n")
        else:
            console.print("[red]✗ Hotel booking failed[/red]\n")
    
    # Book Car
    if trip_details['car_type'] and trip_details['destination'] and trip_details['start_date']:
        console.print("[yellow]🚗 Renting car...[/yellow]")
        
        # Be more explicit with dates to avoid agent confusion
        car_query = f"I need to rent a {trip_details['car_type']} in {trip_details['destination']}. "
        car_query += f"Pickup date is {trip_details['start_date']}. "
        if trip_details['end_date']:
            car_query += f"Return date is {trip_details['end_date']}. "
        car_query += f"Please confirm the booking."
        
        car_messages = await send_to_agent(AGENT_PORTS['car'], car_query)
        if car_messages:
            results['car'] = extract_car_data(car_messages)
            if results['car']:
                console.print("[green]✓ Car rental booked[/green]\n")
            else:
                # Check if agent asked about alternatives
                for msg in car_messages:
                    if 'result' in msg:
                        result = msg['result']
                        if result.get('kind') == 'status-update':
                            status = result.get('status', {})
                            if status.get('state') == 'input-required' and status.get('message'):
                                msg_parts = status['message'].get('parts', [])
                                for part in msg_parts:
                                    if 'text' in part and 'instead' in part.get('text', '').lower():
                                        console.print(f"[yellow]⚠ Car: Vehicle type not available[/yellow]\n")
                                        break
                if not results['car']:
                    console.print("[yellow]⚠ Car response incomplete[/yellow]\n")
        else:
            console.print("[red]✗ Car rental failed[/red]\n")
    
    return results


def display_trip_summary(results, trip_details):
    """Display complete trip summary."""
    
    console.print("\n[bold magenta]═══════════════════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]           🎉 COMPLETE TRIP ITINERARY 🎉           [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════════════════[/bold magenta]\n")
    
    total_cost = 0.0
    
    # Flight Summary
    if results['flight']:
        flight = results['flight']
        console.print("[bold cyan]✈️  FLIGHTS[/bold cyan]")
        console.print("─" * 50)
        
        if 'onward' in flight:
            onward = flight['onward']
            console.print(f"Outbound: {onward['airline']} {onward['flight_number']}")
            console.print(f"  {trip_details['origin']} → {trip_details['destination']}")
            console.print(f"  {onward['date']} | {onward['travel_class']}")
            console.print(f"  ${onward['cost']}\n")
        
        if 'return' in flight:
            ret = flight['return']
            console.print(f"Return: {ret['airline']} {ret['flight_number']}")
            console.print(f"  {trip_details['destination']} → {trip_details['origin']}")
            console.print(f"  {ret['date']} | {ret['travel_class']}")
            console.print(f"  ${ret['cost']}\n")
        
        if 'total_price' in flight:
            total_cost += float(flight['total_price'])
            console.print(f"[bold green]Flight Total: ${flight['total_price']}[/bold green]\n")
    
    # Hotel Summary
    if results['hotel']:
        hotel = results['hotel']
        console.print("\n[bold cyan]🏨 ACCOMMODATION[/bold cyan]")
        console.print("─" * 50)
        
        if 'name' in hotel:
            console.print(f"{hotel['name']}")
        console.print(f"Location: {hotel.get('city', trip_details['destination'])}")
        console.print(f"Room: {hotel.get('room_type', 'N/A')}")
        console.print(f"Check-in: {trip_details['start_date']} at {hotel.get('check_in_time', 'TBD')}")
        console.print(f"Check-out: {trip_details['end_date']} at {hotel.get('check_out_time', 'TBD')}")
        
        if 'price_per_night' in hotel:
            console.print(f"Rate: ${hotel['price_per_night']}/night")
        
        if 'total_rate_usd' in hotel:
            total_cost += float(hotel['total_rate_usd'])
            console.print(f"[bold green]Hotel Total: ${hotel['total_rate_usd']}[/bold green]\n")
    
    # Car Summary
    if results['car']:
        car = results['car']
        console.print("\n[bold cyan]🚗 CAR RENTAL[/bold cyan]")
        console.print("─" * 50)
        
        console.print(f"Vehicle: {car.get('car_type', 'N/A')}")
        console.print(f"Company: {car.get('provider', 'N/A')}")
        console.print(f"Location: {car.get('city', trip_details['destination'])}")
        console.print(f"Pick-up: {car.get('pickup_date', trip_details['start_date'])}")
        console.print(f"Drop-off: {car.get('return_date', trip_details['end_date'])}")
        
        if 'price' in car:
            total_cost += float(car['price'])
            console.print(f"[bold green]Car Total: ${car['price']}[/bold green]\n")
    
    # Grand Total
    if total_cost > 0:
        console.print("\n[bold magenta]═══════════════════════════════════════════════════[/bold magenta]")
        console.print(f"[bold white]GRAND TOTAL: [bold green]${total_cost:.2f}[/bold green][/bold white]")
        console.print("[bold magenta]═══════════════════════════════════════════════════[/bold magenta]\n")


async def main():
    if len(sys.argv) < 2:
        console.print("\n[bold red]Usage:[/bold red]")
        console.print("  python complete_trip.py \"<your trip query>\"\n")
        console.print("[bold cyan]Example:[/bold cyan]")
        console.print('  python complete_trip.py "Business flight from San Francisco to London, Jan 20-27, 2026, 1 adult, book hotel suite, rent SUV"\n')
        console.print("[bold cyan]Another example:[/bold cyan]")
        console.print('  python complete_trip.py "Economy from New York to Paris, Feb 1-8, 2026, 2 adults, AirBnB standard room, 2 guests, rent sedan"\n')
        return
    
    query = " ".join(sys.argv[1:])
    
    console.print(f"\n[bold cyan]Query:[/bold cyan] {query}\n")
    console.print("[dim]Parsing your request...[/dim]\n")
    
    trip_details = parse_trip_query(query)
    
    # Show what was parsed
    console.print("[bold yellow]Detected Trip Details:[/bold yellow]")
    console.print(f"  Route: {trip_details['origin']} → {trip_details['destination']}")
    console.print(f"  Dates: {trip_details['start_date']} to {trip_details['end_date']}")
    console.print(f"  Flight: {trip_details['travel_class']} class, {trip_details['adults']} adult(s)")
    console.print(f"  Hotel: {trip_details['hotel_type']}, {trip_details['room_type']} room, {trip_details['guests']} guest(s)")
    if trip_details['car_type']:
        console.print(f"  Car: {trip_details['car_type']}")
    
    # Book everything
    results = await book_complete_trip(trip_details)
    
    # Display summary
    display_trip_summary(results, trip_details)


if __name__ == "__main__":
    asyncio.run(main())
