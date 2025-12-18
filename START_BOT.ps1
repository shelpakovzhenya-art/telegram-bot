# PowerShell script to start the bot
Write-Host "Starting Telegram Bot..." -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.12+ from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file from .env.example" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if BOT_TOKEN is set
$envContent = Get-Content ".env" -Raw
if ($envContent -match "BOT_TOKEN=your_bot_token_here" -or $envContent -notmatch "BOT_TOKEN=") {
    Write-Host "WARNING: BOT_TOKEN not configured in .env file!" -ForegroundColor Yellow
    Write-Host "Please edit .env and add your bot token" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the bot
Write-Host "Starting bot..." -ForegroundColor Cyan
python -m app.main

