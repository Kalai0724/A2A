# A2A Multi-Agent System Launcher
# This script starts all required services in separate PowerShell windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting A2A Multi-Agent System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the current directory
$currentDir = Get-Location

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file with your GOOGLE_API_KEY" -ForegroundColor Yellow
    exit 1
}

# Read GOOGLE_API_KEY from .env
$apiKey = Get-Content .env | Where-Object { $_ -match "^GOOGLE_API_KEY=" } | ForEach-Object { $_.Split('=')[1] }

if ([string]::IsNullOrEmpty($apiKey)) {
    Write-Host "ERROR: GOOGLE_API_KEY not found in .env file!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Found GOOGLE_API_KEY in .env" -ForegroundColor Green
Write-Host ""

# Function to start a service in a new window
function Start-AgentService {
    param(
        [string]$Title,
        [string]$Cmd,
        [string]$Col
    )
    
    Write-Host "Starting $Title..." -ForegroundColor $Col
    
    $argList = "-NoExit", "-Command", "Set-Location '$currentDir'; `$env:GOOGLE_API_KEY='$apiKey'; `$Host.UI.RawUI.WindowTitle='$Title'; Write-Host '$Title' -ForegroundColor $Col; $Cmd"
    Start-Process powershell -ArgumentList $argList
    Start-Sleep -Seconds 2
}

# Start all services
Write-Host "Launching services (this will take about 15 seconds)..." -ForegroundColor Yellow
Write-Host ""

Start-AgentService -Title "MCP Server (Port 10100)" -Cmd "uv run --env-file .env a2a-mcp --run mcp-server --transport sse" -Col "Magenta"
Start-AgentService -Title "Orchestrator Agent (Port 10101)" -Cmd "uv run --env-file .env src/a2a_mcp/agents/ --agent-card agent_cards/orchestrator_agent.json --port 10101" -Col "Cyan"
Start-AgentService -Title "Planner Agent (Port 10102)" -Cmd "uv run --env-file .env src/a2a_mcp/agents/ --agent-card agent_cards/planner_agent.json --port 10102" -Col "Green"
Start-AgentService -Title "Air Ticketing Agent (Port 10103)" -Cmd "uv run --env-file .env src/a2a_mcp/agents/ --agent-card agent_cards/air_ticketing_agent.json --port 10103" -Col "Yellow"
Start-AgentService -Title "Hotel Booking Agent (Port 10104)" -Cmd "uv run --env-file .env src/a2a_mcp/agents/ --agent-card agent_cards/hotel_booking_agent.json --port 10104" -Col "Blue"
Start-AgentService -Title "Car Rental Agent (Port 10105)" -Cmd "uv run --env-file .env src/a2a_mcp/agents/ --agent-card agent_cards/car_rental_agent.json --port 10105" -Col "DarkCyan"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ All services launched successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services are starting in separate windows..." -ForegroundColor Yellow
Write-Host "Wait about 20-30 seconds for all services to be ready." -ForegroundColor Yellow
Write-Host ""
Write-Host "Then test with:" -ForegroundColor Cyan
Write-Host "  `$env:GOOGLE_API_KEY='$apiKey'; uv run --env-file .env src/a2a_mcp/mcp/client.py --find_agent 'Plan a trip to Paris'" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

