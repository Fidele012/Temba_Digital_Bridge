# ═══════════════════════════════════════════════════════════════
#  Temba Digital Bridge — Full Stack Startup Script
#  Starts: PostgreSQL check → FastAPI backend → ngrok tunnel
#  Run from the project root: .\start-temba.ps1
# ═══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Continue"
$ProjectRoot = $PSScriptRoot
$BackendDir  = Join-Path $ProjectRoot "temba-backend"
$VenvPython  = Join-Path $BackendDir ".venv\Scripts\python.exe"
$VenvUvicorn = Join-Path $BackendDir ".venv\Scripts\uvicorn.exe"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       Temba Digital Bridge — Startup                 ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Kill stale processes ─────────────────────────────────────────────
Write-Host "[ 1/5 ] Cleaning up stale processes..." -ForegroundColor Yellow
Get-Process -Name "ngrok"   -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

# ── Step 2: Check PostgreSQL ──────────────────────────────────────────────────
Write-Host "[ 2/5 ] Checking PostgreSQL..." -ForegroundColor Yellow
$pgRunning = $false
try {
    $result = & $VenvPython -c @"
import asyncio, asyncpg
async def check():
    conn = await asyncpg.connect('postgresql://temba:temba_pass@localhost:5432/temba_db', timeout=5)
    await conn.close()
    print('OK')
asyncio.run(check())
"@ 2>&1
    if ($result -match "OK") {
        Write-Host "  ✓ PostgreSQL connected (temba_db)" -ForegroundColor Green
        $pgRunning = $true
    } else {
        Write-Host "  ✗ PostgreSQL check failed: $result" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ PostgreSQL not reachable: $_" -ForegroundColor Red
}

if (-not $pgRunning) {
    Write-Host ""
    Write-Host "  PostgreSQL must be running before the backend can start." -ForegroundColor Red
    Write-Host "  Start it with one of:" -ForegroundColor White
    Write-Host "    • Docker:  docker-compose -f temba-backend\docker-compose.yml up -d db" -ForegroundColor Gray
    Write-Host "    • Windows: Start the 'postgresql-x64-*' service in Services.msc" -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") { exit 1 }
}

# ── Step 3: Run Alembic migrations ───────────────────────────────────────────
Write-Host "[ 3/5 ] Running database migrations..." -ForegroundColor Yellow
Push-Location $BackendDir
try {
    $migOut = & (Join-Path $BackendDir ".venv\Scripts\alembic.exe") upgrade head 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Migrations up to date" -ForegroundColor Green
    } else {
        Write-Host "  ! Migration output:" -ForegroundColor Yellow
        $migOut | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    }
} catch {
    Write-Host "  ! Could not run migrations: $_" -ForegroundColor Yellow
}
Pop-Location

# ── Step 4: Start FastAPI backend ─────────────────────────────────────────────
Write-Host "[ 4/5 ] Starting FastAPI backend on port 8000..." -ForegroundColor Yellow
$backendProc = Start-Process -FilePath $VenvUvicorn `
    -ArgumentList "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" `
    -WorkingDirectory $BackendDir `
    -PassThru -WindowStyle Normal

Start-Sleep -Seconds 4

# Verify backend is up
$backendOk = $false
for ($i = 0; $i -lt 5; $i++) {
    try {
        $h = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 3 -UseBasicParsing
        if ($h.StatusCode -eq 200) { $backendOk = $true; break }
    } catch { Start-Sleep -Seconds 2 }
}

if ($backendOk) {
    Write-Host "  ✓ Backend running at http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "    API docs: http://127.0.0.1:8000/docs" -ForegroundColor Gray
} else {
    Write-Host "  ✗ Backend did not respond — check the terminal window for errors" -ForegroundColor Red
    Write-Host "    Common causes: DB not running, missing .env, import error" -ForegroundColor Gray
}

# ── Step 5: Start ngrok and print callback URL ────────────────────────────────
Write-Host "[ 5/5 ] Starting ngrok tunnel..." -ForegroundColor Yellow
Start-Process -FilePath "ngrok" -ArgumentList "http 8000" -WindowStyle Hidden
Start-Sleep -Seconds 4

$callbackUrl = $null
for ($i = 0; $i -lt 5; $i++) {
    try {
        $tunnels = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 3
        $pub = ($tunnels.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1).public_url
        if (-not $pub) { $pub = $tunnels.tunnels[0].public_url }
        if ($pub) { $callbackUrl = "$pub/api/v1/ussd/callback"; break }
    } catch { Start-Sleep -Seconds 2 }
}

if ($callbackUrl) {
    Write-Host "  ✓ ngrok tunnel active" -ForegroundColor Green
    Write-Host ""
    Write-Host "┌─────────────────────────────────────────────────────────────────────┐" -ForegroundColor White
    Write-Host "│  USSD Callback URL — paste into Africa's Talking dashboard:          │" -ForegroundColor White
    Write-Host "│                                                                       │" -ForegroundColor White
    Write-Host "│  $callbackUrl" -ForegroundColor Yellow
    Write-Host "│                                                                       │" -ForegroundColor White
    Write-Host "└─────────────────────────────────────────────────────────────────────┘" -ForegroundColor White
    Set-Clipboard -Value $callbackUrl
    Write-Host "  (URL copied to clipboard)" -ForegroundColor Gray
} else {
    Write-Host "  ✗ Could not get ngrok URL. Is ngrok installed and on PATH?" -ForegroundColor Red
    Write-Host "    Install: https://ngrok.com/download" -ForegroundColor Gray
}

Write-Host ""
Write-Host "─────────────────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  How to activate USSD:" -ForegroundColor Cyan
Write-Host "  1. Go to https://account.africastalking.com → Sandbox" -ForegroundColor White
Write-Host "  2. USSD → Manage → Edit your service (*384*36640#)" -ForegroundColor White
Write-Host "  3. Paste the Callback URL above → Save" -ForegroundColor White
Write-Host "  4. Launch the AT Simulator → dial *384*36640#" -ForegroundColor White
Write-Host ""
Write-Host "  Quick links:" -ForegroundColor Cyan
Write-Host "    Backend health : http://127.0.0.1:8000/health" -ForegroundColor Gray
Write-Host "    API docs       : http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host "    ngrok inspector: http://127.0.0.1:4040" -ForegroundColor Gray
Write-Host "─────────────────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

# ── Test the USSD endpoint directly ──────────────────────────────────────────
if ($backendOk) {
    Write-Host "  Running local USSD smoke test..." -ForegroundColor Yellow
    try {
        $testBody = "sessionId=test-local&serviceCode=*384*36640%23&phoneNumber=%2B250700000000&text="
        $testResp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/ussd/callback" `
            -Method POST -Body $testBody `
            -ContentType "application/x-www-form-urlencoded" `
            -TimeoutSec 5 -UseBasicParsing
        $body = $testResp.Content
        if ($body -match "^(CON|END)") {
            Write-Host "  ✓ USSD endpoint responding correctly:" -ForegroundColor Green
            Write-Host "    $($body.Split("`n")[0])" -ForegroundColor Gray
        } else {
            Write-Host "  ! Unexpected USSD response: $body" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ! USSD smoke test failed: $_" -ForegroundColor Yellow
    }
    Write-Host ""
}
