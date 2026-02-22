@echo off
echo ========================================
echo Starting LinkFlow Admin Panel (Local)
echo ========================================
echo.
echo Admin Panel: http://localhost:5000
echo API Server: http://localhost:5001
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

cd admin
start "LinkFlow Admin" python admin_panel_db.py
timeout /t 3 /nobreak >nul
start "LinkFlow API" python api_server.py

echo.
echo Both servers started!
echo Open http://localhost:5000 in your browser
echo.
pause
