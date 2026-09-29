# SourceMind Launch Script
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Starting SourceMind (Backend + Frontend)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Start Backend
Write-Host "`n[1/2] Starting Flask Backend on http://127.0.0.1:5000..." -ForegroundColor Yellow
$backendProcess = Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "-m backend.app" -PassThru

# Start Frontend
Write-Host "[2/2] Starting React + Vite Frontend on http://127.0.0.1:5173..." -ForegroundColor Green
Set-Location frontend
npm.cmd run dev -- --host 127.0.0.1 --port 5173
