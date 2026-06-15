# Temba USSD Startup Script
# Run this every time you want to use the USSD system.
# It starts ngrok and prints the callback URL to paste into Africa's Talking.

Write-Host "`n=== Temba USSD Startup ===" -ForegroundColor Cyan

# Kill any existing ngrok processes
Get-Process -Name "ngrok" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

# Start ngrok in the background
Write-Host "Starting ngrok tunnel on port 8000..." -ForegroundColor Yellow
Start-Process -FilePath "ngrok" -ArgumentList "http 8000" -WindowStyle Hidden
Start-Sleep -Seconds 4

# Fetch public URL from ngrok local API
try {
    $tunnels = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels"
    $url = ($tunnels.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1).public_url
    if (-not $url) { $url = $tunnels.tunnels[0].public_url }

    $callbackUrl = "$url/api/v1/ussd/callback"

    Write-Host "`n✓ ngrok tunnel active" -ForegroundColor Green
    Write-Host "`n┌─────────────────────────────────────────────────────────────────┐" -ForegroundColor White
    Write-Host "│  USSD Callback URL (paste into Africa's Talking dashboard):      │" -ForegroundColor White
    Write-Host "│                                                                   │" -ForegroundColor White
    Write-Host "│  $callbackUrl" -ForegroundColor Yellow
    Write-Host "│                                                                   │" -ForegroundColor White
    Write-Host "└─────────────────────────────────────────────────────────────────┘" -ForegroundColor White

    Write-Host "`nSteps to activate:" -ForegroundColor Cyan
    Write-Host "  1. Go to: https://account.africastalking.com" -ForegroundColor White
    Write-Host "  2. Switch to Sandbox environment (top-right dropdown)" -ForegroundColor White
    Write-Host "  3. USSD → Manage → Edit service → paste the URL above as Callback URL" -ForegroundColor White
    Write-Host "  4. Save, then use the AT Simulator to dial *384*36640#" -ForegroundColor White

    # Copy to clipboard
    Set-Clipboard -Value $callbackUrl
    Write-Host "`n(URL copied to clipboard)" -ForegroundColor Gray

} catch {
    Write-Host "ERROR: Could not get ngrok URL. Is ngrok installed?" -ForegroundColor Red
    Write-Host $_ -ForegroundColor Red
}

Write-Host "`nngrok inspector: http://127.0.0.1:4040" -ForegroundColor Gray
Write-Host "API health:      http://127.0.0.1:8000/health" -ForegroundColor Gray
Write-Host ""
