"""
Client to send trip planning requests to the Orchestrator Agent.
This actually processes the request through the full A2A workflow.
"""
import asyncio
import json
import sys
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

async def send_request_to_orchestrator(query: str, orchestrator_url: str = "http://localhost:10101"):
    """Send a request to the orchestrator agent and get the full response."""
    
    console.print(Panel.fit(
        f"[cyan]Sending query to Orchestrator Agent:[/cyan]\n[white]{query}[/white]",
        border_style="cyan"
    ))
    
    # A2A JSON-RPC SendStreamingMessage request format
    import uuid
    request_payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/stream",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [
                    {
                        "text": query
                    }
                ]
            }
        }
    }
    
    console.print("\n[yellow]⏳ Processing request through A2A workflow...[/yellow]\n")
    console.print("[dim]This may take 30-60 seconds as the orchestrator:[/dim]")
    console.print("[dim]  1. Calls the Planner to create a plan[/dim]")
    console.print("[dim]  2. Discovers agents via MCP[/dim]")
    console.print("[dim]  3. Executes tasks through multiple agents[/dim]")
    console.print("[dim]  4. Aggregates and summarizes results[/dim]\n")
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            # A2A protocol uses POST to root endpoint with JSON-RPC
            response = await client.post(
                orchestrator_url,
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
                    return None
                
                # Check for JSON-RPC error in any message
                for msg in messages:
                    if 'error' in msg:
                        console.print(f"[red]✗ A2A Error: {msg['error']}[/red]")
                        return None
                
                console.print(Panel.fit(
                    "[green]✓ Request Processed Successfully![/green]",
                    border_style="green"
                ))
                
                # Display the messages
                console.print(f"\n[bold cyan]Received {len(messages)} message(s) from orchestrator:[/bold cyan]\n")
                
                # Extract and display results
                summary_found = False
                for i, msg in enumerate(messages, 1):
                    if 'result' in msg:
                        result = msg['result']
                        # Look for summary in status updates or artifacts
                        if result.get('kind') == 'status-update' and result.get('final'):
                            status_msg = result.get('status', {}).get('message')
                            if status_msg and 'parts' in status_msg:
                                for part in status_msg['parts']:
                                    if 'text' in part:
                                        console.print(Panel.fit(
                                            part['text'],
                                            title="[bold green]Trip Summary[/bold green]",
                                            border_style="green"
                                        ))
                                        summary_found = True
                        elif 'content' in result:
                            # Error message or direct content
                            console.print(f"[yellow]Message {i}:[/yellow] {result['content']}")
                
                # If no summary found, show all messages
                if not summary_found:
                    console.print("\n[yellow]Full response (no summary found):[/yellow]")
                    for i, msg in enumerate(messages, 1):
                        console.print(f"\n[dim]Message {i}:[/dim]")
                        console.print(json.dumps(msg, indent=2))
                
                return messages
            else:
                console.print(f"[red]✗ Error: {response.status_code}[/red]")
                console.print(response.text)
                return None
                
    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to Orchestrator Agent at {orchestrator_url}[/red]")
        console.print("[yellow]Make sure all agents are running (use start_all.ps1)[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return None


async def main():
    """Main function to test the trip planning system."""
    
    # Default query or from command line
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "I need to book a flight from San Francisco to London, departing January 20, 2026 and returning January 27, 2026"
    
    console.print("\n[bold magenta]═══════════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]   A2A Multi-Agent Trip Planning System   [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════════[/bold magenta]\n")
    
    result = await send_request_to_orchestrator(query)
    
    if result:
        console.print("\n[green]✓ Test completed successfully![/green]")
    else:
        console.print("\n[red]✗ Test failed[/red]")


if __name__ == "__main__":
    asyncio.run(main())
