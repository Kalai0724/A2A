"""
Quick flight booking script - use from command line.
Usage: uv run book_flight.py "your query here"
"""
import asyncio
import json
import sys
import uuid
import httpx
import sqlite3
from rich.console import Console
from rich.panel import Panel
from datetime import datetime
import re

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("FLIGHT_API_KEY")

console = Console()

def parse_flight_query(query: str):
    # Default values
    origin = "San Francisco"
    destination = "London"
    departure_date = "2026-01-20"
    return_date = "2026-01-27"
    travel_class = "ECONOMY"
    # Class
    if "business" in query.lower():
        travel_class = "BUSINESS"
    elif "economy" in query.lower():
        travel_class = "ECONOMY"
    # Origin
    from_match = re.search(r'from\s+([a-zA-Z\s]+?)\s+to', query, re.IGNORECASE)
    if from_match:
        origin = from_match.group(1).strip()
    # Destination
    to_match = re.search(r'to\s+([a-zA-Z\s]+?)[,\s]', query, re.IGNORECASE)
    if to_match:
        destination = to_match.group(1).strip()
    # Dates
    date_match = re.search(r'(\w+\s\d{1,2}),?\s*-\s*(\w+\s\d{1,2}),?\s*(\d{4})', query)
    if date_match:
        dep = date_match.group(1)
        ret = date_match.group(2)
        year = date_match.group(3)
        departure_date = f"{dep}, {year}"
        return_date = f"{ret}, {year}"
        # Convert to YYYY-MM-DD
        try:
            departure_date = str(datetime.strptime(departure_date, "%b %d, %Y").date())
            return_date = str(datetime.strptime(return_date, "%b %d, %Y").date())
        except Exception:
            try:
                departure_date = str(datetime.strptime(departure_date, "%B %d, %Y").date())
                return_date = str(datetime.strptime(return_date, "%B %d, %Y").date())
            except Exception:
                pass
    return origin, destination, departure_date, return_date, travel_class

async def book_flight(query: str):
    """Send flight booking request and display results from local DB."""
    origin, destination, departure_date, return_date, travel_class = parse_flight_query(query)
    # Always resolve DB path relative to this script's location
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'travel_agency.db'))
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Find onward flight (case-insensitive)
    c.execute("""
        SELECT flight_number, airline, origin, destination, date, travel_class, cost
        FROM flights
        WHERE lower(origin)=lower(?) AND lower(destination)=lower(?) AND date=? AND lower(travel_class)=lower(?)
    """, (origin, destination, departure_date, travel_class))
    onward = c.fetchone()
    # Find return flight (case-insensitive)
    c.execute("""
        SELECT flight_number, airline, origin, destination, date, travel_class, cost
        FROM flights
        WHERE lower(origin)=lower(?) AND lower(destination)=lower(?) AND date=? AND lower(travel_class)=lower(?)
    """, (destination, origin, return_date, travel_class))
    ret = c.fetchone()
    
    if onward and ret:
        total_price = onward[6] + ret[6]
        console.print(Panel.fit("[bold green]\u2713 Flight Booking Complete![/bold green]", border_style="green"))
        console.print(f"\n[bold cyan]Outbound:[/bold cyan] {onward[1]} {onward[0]} | {onward[2]} → {onward[3]} | {onward[4]} | {onward[5]} | ${onward[6]}")
        console.print(f"[bold cyan]Return:[/bold cyan] {ret[1]} {ret[0]} | {ret[2]} → {ret[3]} | {ret[4]} | {ret[5]} | ${ret[6]}")
        console.print(f"\n[bold green]Total Price: ${total_price}[/bold green]")
        conn.close()
        return True
    else:
        console.print("[yellow]No matching flights found in local database.[/yellow]")
        # Print all flights for debugging
        console.print("[bold]Available flights in DB:[/bold]")
        c.execute("SELECT flight_number, airline, origin, destination, date, travel_class, cost FROM flights")
        all_flights = c.fetchall()
        for f in all_flights:
            console.print(f"{f[1]} {f[0]} | {f[2]} → {f[3]} | {f[4]} | {f[5]} | ${f[6]}")
        conn.close()
        return False


async def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Default query with all details
        query = """Book a round-trip flight from San Francisco to London, 
departing January 20, 2026, returning January 27, 2026, Economy class, 1 adult."""
    
    console.print("\n[bold magenta]═══════════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]        Flight Booking Assistant        [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════════[/bold magenta]\n")
    
    await book_flight(query)


if __name__ == "__main__":
    asyncio.run(main())
