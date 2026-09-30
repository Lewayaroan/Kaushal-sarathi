@echo off
title Kaushal Sarathi - One-Click Launcher
echo ======================================================================
echo    Launching Kaushal Sarathi (कौशल सारथी) Prototype
echo    Ministry of Social Justice and Empowerment (MoSJE) - PM-AJAY GIA
echo ======================================================================
echo.

cd /d "%~dp0"

:: Check if python is available
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [NOTICE] Python was not found in system PATH.
    echo Launching autonomous frontend directly in your default browser...
    echo.
    start "" "%~dp0frontend\index.html"
    echo ======================================================================
    echo  Prototype is active!
    echo  - Autonomous Voice AI, NSQF Mapping, GIA Grant Calculator,
    echo    WhatsApp QR Kaushal Card, and DM Heatmap are fully functional!
    echo ======================================================================
    echo.
    pause
    exit /b 0
)

echo [1/4] Starting FastAPI Backend on port 8000...
start "Kaushal Sarathi Backend (FastAPI)" cmd /k "python -m uvicorn backend.main:app --port 8000 --reload"

echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo [2/4] Starting Frontend Web Server on port 3000...
start "Kaushal Sarathi Frontend (HTTP Server)" cmd /k "python -m http.server 3000 --directory frontend"

echo Waiting for frontend to initialize...
timeout /t 2 /nobreak >nul

echo [3/4] Initializing demo data...
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:8000/api/system/seed?force=true' -Method Post | Out-Null; Write-Host '  -> Demo data successfully initialized!' -ForegroundColor Green } catch { Write-Host '  -> Backend starting up...' }"

echo [4/4] Opening Web Application in your default browser...
start http://localhost:3000

echo.
echo ======================================================================
echo  Kaushal Sarathi Prototype is ACTIVE!
echo  - Frontend Web App: http://localhost:3000
echo  - Backend REST API: http://localhost:8000/docs
echo ======================================================================
echo.
pause
