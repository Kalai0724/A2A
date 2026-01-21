"""
Test individual agents directly (bypassing the orchestrator).
"""
import asyncio
import json
import sys
import uuid
import httpx
from rich.console import Console
from rich.panel import Panel

console = Console()

async def test_agent(agent_name: str, port: int, query: str):
    """Test an agent directly."""
    
    console.print(Panel.fit(
        f"[cyan]Testing {agent_name} on port {port}[/cyan]\n[white]{query}[/white]",
        border_style="cyan"
    ))
    
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
    
    console.print("\n[yellow]⏳ Sending request...[/yellow]\n")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"http://localhost:{port}",
                json=request_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                # Handle SSE format (Server-Sent Events)
                response_text = response.text.strip()
                
                # Parse SSE format: extract JSON from "data: {...}" lines
                messages = []
                for line in response_text.split('\n'):
                    if line.startswith('data: '):
                        json_str = line[6:]  # Remove "data: " prefix
                        try:
                            msg = json.loads(json_str)
                            messages.append(msg)
                        except json.JSONDecodeError:
                            continue
                
                if not messages:
                    console.print(f"[red]✗ No valid messages in response[/red]")
                    return False
                
                console.print(Panel.fit("[green]✓ Success![/green]", border_style="green"))
                console.print(f"\n[bold cyan]Received {len(messages)} message(s):[/bold cyan]\n")
                
                for i, msg in enumerate(messages, 1):
                    console.print(f"[yellow]Message {i}:[/yellow]")
                    console.print(json.dumps(msg, indent=2))
                    console.print()
                
                return True
            else:
                console.print(f"[red]✗ HTTP {response.status_code}[/red]")
                console.print(response.text)
                return False
                
    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to agent on port {port}[/red]")
        console.print("[yellow]Make sure the agent is running[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


async def main():
    console.print("\n[bold magenta]═══════════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]   Testing Individual A2A Agents   [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════════[/bold magenta]\n")
    
    tests = [
        ("Air Ticketing Agent", 10103, "Find flights from San Francisco to London departing January 20, 2026 and returning January 27, 2026"),
        ("Hotel Booking Agent", 10104, "Find hotels in London for January 20-27, 2026"),
        ("Car Rental Agent", 10105, "Find rental cars in London for January 20-27, 2026"),
    ]
    
    results = []
    for agent_name, port, query in tests:
        success = await test_agent(agent_name, port, query)
        results.append((agent_name, success))
        console.print("\n" + "="*80 + "\n")
    
    console.print("\n[bold]Summary:[/bold]")
    for agent_name, success in results:
        status = "[green]✓[/green]" if success else "[red]✗[/red]"
        console.print(f"{status} {agent_name}")


if __name__ == "__main__":
    asyncio.run(main())
