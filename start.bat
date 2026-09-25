@echo off
title Karigar Connect - One-Click Launcher
echo ===================================================
echo    Launching Karigar Connect Prototype (SIH 2026)
echo ===================================================
echo.

cd /d "%~dp0"

echo [1/4] Starting FastAPI Backend on port 8000...
start "Karigar Backend (FastAPI)" cmd /k "python -m uvicorn backend.main:app --port 8000 --reload"

echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo [2/4] Starting Frontend Web Server on port 3000...
start "Karigar Frontend (HTTP Server)" cmd /k "python -m http.server 3000 --directory frontend"

echo Waiting for frontend to initialize...
timeout /t 2 /nobreak >nul

echo [3/4] Initializing demo data...
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:8000/api/system/seed?force=true' -Method Post | Out-Null; Write-Host '  -> Demo data successfully initialized!' -ForegroundColor Green } catch { Write-Host '  -> Backend starting up...' }"

echo [4/4] Opening Web Application in your default browser...
start http://localhost:3000

echo.
echo ===================================================
echo  Prototype is active!
echo  - Frontend: http://localhost:3000
echo  - Backend API: http://localhost:8000
echo  - Keep the two backend/frontend windows open!
echo ===================================================
echo.
pause
