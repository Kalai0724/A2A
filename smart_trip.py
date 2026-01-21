"""
Smart Trip Planner - Automatically handles agent questions to complete ALL bookings.
This version detects when agents ask questions and automatically responds "yes" to alternatives.
"""

import asyncio
import json
import sys
import uuid
import httpx
from rich.console import Console
from rich.panel import Panel
import re
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("smart_trip.log", mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("smart_trip")

console = Console()

AGENT_PORTS = {
    "flight": 10103,
    "hotel": 10104,
    "car": 10105
}

async def send_to_agent(port: int, query: str, context_id: str = None, max_rounds: int = 5):
    """Send query to agent and auto-handle follow-up questions."""
    
    logger.info(f"[send_to_agent] BEGIN agent interaction for port {port} with query: {query}")
    for round_num in range(max_rounds):
        message_params = {
            "messageId": str(uuid.uuid4()),
            "role": "user",
            "parts": [{"text": query}]
        }

        if context_id:
            message_params["contextId"] = context_id

        request_payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "message/stream",
            "params": {"message": message_params}
        }

        logger.info(f"[send_to_agent] Sending to port {port} (round {round_num+1}): {query}")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"http://localhost:{port}",
                    json=request_payload,
                    headers={"Content-Type": "application/json"}
                )

                logger.info(f"[send_to_agent] Response status: {response.status_code}")
                if response.status_code != 200:
                    logger.error(f"[send_to_agent] Non-200 response: {response.status_code} {response.text}")
                    return None, None, False

                messages = []
                for line in response.text.strip().split('\n'):
                    if line.startswith('data: '):
                        try:
                            msg = json.loads(line[6:])
                            messages.append(msg)
                        except Exception as ex:
                            logger.warning(f"[send_to_agent] Failed to parse line: {line} | Error: {ex}")
                            continue

                logger.info(f"[send_to_agent] Parsed {len(messages)} messages from agent: {messages}")

                # Check what we got
                new_context_id = None
                has_data = False
                needs_input = False

                for msg in messages:
                    logger.info(f"[send_to_agent] Agent message: {msg}")
                    if 'result' in msg:
                        result = msg['result']
                        logger.info(f"[send_to_agent] Agent result: {result}")
                        if 'contextId' in result:
                            new_context_id = result['contextId']

                        # Check if completed with actual data
                        if result.get('kind') == 'artifact-update':
                            artifact = result.get('artifact', {})
                            logger.info(f"[send_to_agent] Artifact: {artifact}")
                            for part in artifact.get('parts', []):
                                logger.info(f"[send_to_agent] Artifact part: {part}")
                                if 'data' in part:
                                    logger.info(f"[send_to_agent] Booking data received from agent on port {port}.")
                                    return messages, new_context_id, True

                                # Check if it's just a question in text
                                if 'text' in part:
                                    text = part.get('text', '').lower()
                                    logger.info(f"[send_to_agent] Agent asked: {text}")
                                    if any(word in text for word in ['instead?', 'would you like', 'choose from', 'not supported']):
                                        needs_input = True

                        # Check if agent is asking a question via status
                        if result.get('kind') == 'status-update':
                            status = result.get('status', {})
                            logger.info(f"[send_to_agent] Status: {status}")
                            if status.get('state') == 'input-required':
                                needs_input = True

                # If agent needs input, answer and continue
                if needs_input and round_num < max_rounds - 1:
                    logger.info(f"[send_to_agent] Agent asked a question, auto-answering 'yes'.")
                    console.print(f"[dim]  → Agent asked question, auto-answering 'yes'...[/dim]")
                    query = "yes"
                    context_id = new_context_id
                    await asyncio.sleep(1)  # Give agent time
                    continue  # Go to next round

                # No data and no question = failed
                logger.warning(f"[send_to_agent] No booking data and no further question from agent on port {port}.")
                return messages, new_context_id, False

        except Exception as e:
            logger.error(f"[send_to_agent] Exception: {e}")
            console.print(f"[dim]  → Error: {e}[/dim]")
            return None, None, False

    # Max rounds reached without success
    logger.error(f"[send_to_agent] Max rounds reached without success for port {port}.")
    return messages if 'messages' in locals() else None, new_context_id if 'new_context_id' in locals() else None, False


def parse_trip_query(query: str):
    """Parse combined trip query."""
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
    
    # Try short format
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
    if 'business' in query_lower:
        travel_class = "BUSINESS"
    elif 'first' in query_lower:
        travel_class = "FIRST"
    
    # Extract adults
    adults_match = re.search(r'(\d+)\s*adults?', query_lower)
    adults = adults_match.group(1) if adults_match else "1"
    
    # Extract room type (use valid values only)
    room_type = "STANDARD"
    if 'suite' in query_lower:
        room_type = "SUITE"
    elif 'single' in query_lower:
        room_type = "SINGLE"
    elif 'double' in query_lower:
        room_type = "DOUBLE"
    
    guests = adults
    
    # Extract car type
    car_type = None
    if 'suv' in query_lower:
        car_type = "SUV"
    elif 'sedan' in query_lower:
        car_type = "SEDAN"
    elif 'truck' in query_lower:
        car_type = "TRUCK"
    
    return {
        'origin': origin,
        'destination': destination,
        'start_date': start_date,
        'end_date': end_date,
        'travel_class': travel_class,
        'adults': adults,
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
    """Book all three components with auto-answer for questions."""
    
    console.print("\n[bold cyan]🌍 Smart Trip Planning (Auto-handling agent questions)...[/bold cyan]\n")
    logger.info("[book_complete_trip] Starting booking process for trip: %s", trip_details)

    results = {'flight': None, 'hotel': None, 'car': None}

    # Book Flight
    if trip_details['origin'] and trip_details['destination'] and trip_details['start_date']:
        console.print("[yellow]✈️  Booking flights...[/yellow]")
        flight_query = f"Book {trip_details['travel_class'].lower()} flight from {trip_details['origin']} to {trip_details['destination']}, "
        flight_query += f"departing {trip_details['start_date']}, "
        if trip_details['end_date']:
            flight_query += f"returning {trip_details['end_date']}, "
        flight_query += f"{trip_details['adults']} adult"

        logger.info(f"[book_complete_trip] Sending flight booking query: {flight_query}")
        messages, context_id, success = await send_to_agent(AGENT_PORTS['flight'], flight_query)
        logger.info(f"[book_complete_trip] Flight agent returned: success={success}, messages={messages}")
        if success and messages:
            results['flight'] = extract_flight_data(messages)
            logger.info(f"[book_complete_trip] Flight booking data: {results['flight']}")
            console.print("[green]✓ Flight booked successfully[/green]\n")
        else:
            logger.warning(f"[book_complete_trip] Flight booking failed. Messages: {messages}")
            logger.error(f"[book_complete_trip] FLIGHT BOOKING FAILED. Query: {flight_query} | Messages: {messages}")
            console.print("[red]✗ Flight booking failed[/red]\n")

    # Book Hotel
    if trip_details['destination'] and trip_details['start_date'] and trip_details['end_date']:
        console.print("[yellow]🏨 Booking hotel...[/yellow]")
        hotel_query = f"Book a hotel in {trip_details['destination']}. "
        hotel_query += f"Check-in date: {trip_details['start_date']}. "
        hotel_query += f"Check-out date: {trip_details['end_date']}. "
        hotel_query += f"Hotel type: HOTEL. "
        hotel_query += f"Room type: {trip_details['room_type']}. "
        hotel_query += f"Number of guests: {trip_details['guests']}. "
        hotel_query += f"Please confirm."

        logger.info(f"[book_complete_trip] Sending hotel booking query: {hotel_query}")
        messages, context_id, success = await send_to_agent(AGENT_PORTS['hotel'], hotel_query)
        logger.info(f"[book_complete_trip] Hotel agent returned: success={success}, messages={messages}")
        if success and messages:
            results['hotel'] = extract_hotel_data(messages)
            logger.info(f"[book_complete_trip] Hotel booking data: {results['hotel']}")
            console.print("[green]✓ Hotel booked successfully[/green]\n")
        else:
            logger.warning(f"[book_complete_trip] Hotel booking failed. Messages: {messages}")
            logger.error(f"[book_complete_trip] HOTEL BOOKING FAILED. Query: {hotel_query} | Messages: {messages}")
            console.print("[red]✗ Hotel booking failed[/red]\n")

    # Book Car
    if trip_details['car_type'] and trip_details['destination'] and trip_details['start_date']:
        console.print("[yellow]🚗 Renting car...[/yellow]")
        car_query = f"I need to rent a {trip_details['car_type']} in {trip_details['destination']}. "
        car_query += f"Pickup date is {trip_details['start_date']}. "
        if trip_details['end_date']:
            car_query += f"Return date is {trip_details['end_date']}. "
        car_query += f"Confirm booking."

        logger.info(f"[book_complete_trip] Sending car rental query: {car_query}")
        messages, context_id, success = await send_to_agent(AGENT_PORTS['car'], car_query)
        logger.info(f"[book_complete_trip] Car agent returned: success={success}, messages={messages}")
        if success and messages:
            results['car'] = extract_car_data(messages)
            logger.info(f"[book_complete_trip] Car rental booking data: {results['car']}")
            console.print("[green]✓ Car rental booked successfully[/green]\n")
        else:
            logger.warning(f"[book_complete_trip] Car rental booking failed. Messages: {messages}")
            logger.error(f"[book_complete_trip] CAR BOOKING FAILED. Query: {car_query} | Messages: {messages}")
            console.print("[red]✗ Car rental failed[/red]\n")

    logger.info(f"[book_complete_trip] Booking results: {results}")
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
    else:
        console.print("\n[yellow]⚠ No bookings completed. Try a different route or dates.[/yellow]\n")


async def main():
    if len(sys.argv) < 2:
        console.print("\n[bold red]Usage:[/bold red]")
        console.print("  python smart_trip.py \"<your trip query>\"\n")
        console.print("[bold cyan]Examples:[/bold cyan]")
        console.print('  python smart_trip.py "Business from San Francisco to London, Jan 20-27, 2026, 1 adult, book suite, rent SUV"')
        console.print('  python smart_trip.py "Economy from New York to Paris, Feb 1-8, 2026, 2 adults, book standard room, rent SUV"\n')
        return

    query = " ".join(sys.argv[1:])
    logger.info(f"[main] Received query: {query}")

    console.print(f"\n[bold cyan]Query:[/bold cyan] {query}\n")
    console.print("[dim]Parsing your request...[/dim]\n")

    trip_details = parse_trip_query(query)
    logger.info(f"[main] Parsed trip details: {trip_details}")

    console.print("[bold yellow]Trip Details:[/bold yellow]")
    console.print(f"  {trip_details['origin']} → {trip_details['destination']}")
    console.print(f"  {trip_details['start_date']} to {trip_details['end_date']}")
    console.print(f"  {trip_details['travel_class']} class, {trip_details['adults']} adult(s)")
    console.print(f"  {trip_details['room_type']} room, {trip_details['guests']} guest(s)")
    if trip_details['car_type']:
        console.print(f"  {trip_details['car_type']} rental")

    results = await book_complete_trip(trip_details)
    logger.info(f"[main] Final booking results: {results}")
    display_trip_summary(results, trip_details)


if __name__ == "__main__":
    asyncio.run(main())
