# PowerShell script to run LinkFlow Admin locally

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting LinkFlow Admin Panel (Local)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Admin Panel: http://localhost:5000" -ForegroundColor Green
Write-Host "API Server: http://localhost:5001" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Admin Panel
$adminJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    cd admin
    python admin_panel_db.py
}

Start-Sleep -Seconds 2

# Start API Server
$apiJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    cd admin
    python api_server.py
}

Write-Host "Both servers started!" -ForegroundColor Green
Write-Host "Admin Panel PID: $($adminJob.Id)" -ForegroundColor Gray
Write-Host "API Server PID: $($apiJob.Id)" -ForegroundColor Gray
Write-Host ""
Write-Host "Open http://localhost:5000 in your browser" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to stop servers..." -ForegroundColor Red

# Wait for user input
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Stop jobs
Write-Host ""
Write-Host "Stopping servers..." -ForegroundColor Yellow
Stop-Job -Job $adminJob, $apiJob
Remove-Job -Job $adminJob, $apiJob
Write-Host "Servers stopped!" -ForegroundColor Green
