"""
Test the Planner Agent to see how it breaks down trip requests.
"""
import asyncio
import json
import uuid
import httpx
from rich.console import Console
from rich.panel import Panel

console = Console()

async def test_planner(query: str):
    """Test the planner agent."""
    
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
    
    console.print("\n[bold magenta]═══════════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]        Planner Agent Test           [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════════[/bold magenta]\n")
    
    console.print(Panel(query, title="[bold]Your Trip Request[/bold]", border_style="cyan"))
    console.print("\n[yellow]⏳ Planner is analyzing your request...[/yellow]\n")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:10102",
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
                
                # Extract plan
                for msg in messages:
                    if 'result' in msg:
                        result = msg['result']
                        
                        if result.get('kind') == 'artifact-update':
                            artifact = result.get('artifact', {})
                            
                            for part in artifact.get('parts', []):
                                if 'data' in part:
                                    plan_data = part['data']
                                    
                                    console.print(Panel.fit(
                                        "[bold green]✓ Plan Created![/bold green]",
                                        border_style="green"
                                    ))
                                    
                                    # Display trip info
                                    if 'trip_info' in plan_data:
                                        trip = plan_data['trip_info']
                                        console.print("\n[bold cyan]Trip Information:[/bold cyan]")
                                        for key, value in trip.items():
                                            console.print(f"  {key}: {value}")
                                    
                                    # Display tasks
                                    if 'tasks' in plan_data:
                                        console.print("\n[bold cyan]Planned Tasks:[/bold cyan]")
                                        for i, task in enumerate(plan_data['tasks'], 1):
                                            console.print(f"\n[yellow]{i}. {task.get('name', 'Task')}[/yellow]")
                                            console.print(f"   {task.get('description', '')}")
                                            if 'agent' in task:
                                                console.print(f"   [dim]→ Agent: {task['agent']}[/dim]")
                                
                                elif 'text' in part:
                                    console.print(f"\n[cyan]Planner:[/cyan] {part['text']}")
                
                return True
            else:
                console.print(f"[red]✗ HTTP {response.status_code}[/red]")
                return False
                
    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to Planner Agent on port 10102[/red]")
        console.print("[yellow]Make sure agents are running: .\\start_all.ps1[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return False


async def main():
    queries = [
        "Plan a complete trip to Paris from New York, February 1-8, 2026",
        "I need to travel to London for business, January 20-27, 2026, from San Francisco",
        "Plan a family vacation to Tokyo, March 15-22, 2026, departing from Los Angeles, need hotel and rental car",
    ]
    
    console.print("\n[bold cyan]Choose a trip scenario:[/bold cyan]")
    for i, q in enumerate(queries, 1):
        console.print(f"{i}. {q}")
    
    choice = input("\nEnter choice (1-3) or custom query: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(queries):
        query = queries[int(choice) - 1]
    else:
        query = choice if choice else queries[0]
    
    await test_planner(query)


if __name__ == "__main__":
    asyncio.run(main())
