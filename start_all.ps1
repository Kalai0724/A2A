# A2A Multi-Agent System Launcher
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting A2A Multi-Agent System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$workDir = $PSScriptRoot

# Read API key from .env
$apiKey = (Get-Content "$workDir\.env" | Where-Object { $_ -match "^GOOGLE_API_KEY=" }).Split('=')[1]

if ([string]::IsNullOrEmpty($apiKey)) {
    Write-Host "ERROR: GOOGLE_API_KEY not found in .env!" -ForegroundColor Red
    exit 1
}

Write-Host "Found GOOGLE_API_KEY" -ForegroundColor Green
Write-Host ""
Write-Host "Launching 6 services in separate windows..." -ForegroundColor Yellow
Write-Host ""

# MCP Server
Write-Host "[1/6] Starting MCP Server..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoExit -Command cd '$workDir'; `$env:GOOGLE_API_KEY='$apiKey'; uv run --env-file .env a2a-mcp --run mcp-server --transport sse"
Start-Sleep 3

# Orchestrator
Write-Host "[2/6] Starting Orchestrator Agent..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command cd '$workDir'; `$env:GOOGLE_API_KEY='$apiKey'; uv run --env-file .env src/a2a_mcp/agents/ --agent-card agent_cards/orchestrator_agent.json --port 10101"
Start-Sleep 2

# Planner
Write-Host "[3/6] Starting Planner Agent..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command cd '$workDir'; `$env:GOOGLE_API_KEY='$apiKey'; uv run --env-file .env src/a2a_mcp/agents/ --agent-card agent_cards/planner_agent.json --port 10102"
Start-Sleep 2

# Air Ticketing
Write-Host "[4/6] Starting Air Ticketing Agent..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command cd '$workDir'; `$env:GOOGLE_API_KEY='$apiKey'; uv run --env-file .env src/a2a_mcp/agents/ --agent-card agent_cards/air_ticketing_agent.json --port 10103"
Start-Sleep 2

# Hotel Booking
Write-Host "[5/6] Starting Hotel Booking Agent..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit -Command cd '$workDir'; `$env:GOOGLE_API_KEY='$apiKey'; uv run --env-file .env src/a2a_mcp/agents/ --agent-card agent_cards/hotel_booking_agent.json --port 10104"
Start-Sleep 2

# Car Rental
Write-Host "[6/6] Starting Car Rental Agent..." -ForegroundColor DarkCyan
Start-Process powershell -ArgumentList "-NoExit -Command cd '$workDir'; `$env:GOOGLE_API_KEY='$apiKey'; uv run --env-file .env src/a2a_mcp/agents/ --agent-card agent_cards/car_rental_agent.json --port 10105"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "All services launched!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Wait 20-30 seconds for all services to initialize." -ForegroundColor Yellow
Write-Host ""
Write-Host "Then test with:" -ForegroundColor Cyan
Write-Host "  `$env:GOOGLE_API_KEY='$apiKey'; uv run src/a2a_mcp/mcp/client.py --find_agent 'I need to book a flight'" -ForegroundColor White
Write-Host ""
