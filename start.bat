@echo off
setlocal
title Exchange Rate Dashboard Launcher

echo ===================================================
echo      Exchange Rate Dashboard - One-Click Start
echo ===================================================
echo.

:: 1. Check for .env file
if not exist .env (
    echo [ERROR] .env file not found!
    echo ---------------------------------------------------
    echo Please rename '.env.example' to '.env' and configure
    echo your API keys before running this script.
    echo ---------------------------------------------------
    pause
    exit /b 1
)

:: 2. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: 3. Optional: Check/Install dependencies
:: Uncomment the lines below if you want to auto-install dependencies
:: echo [INFO] Checking dependencies...
:: pip install -r requirements.txt >nul 2>&1

:: 4. Open Browser (Async)
echo [INFO] Opening browser...
:: Wait 3 seconds to let the server start, then open browser
start /b cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:8000"

:: 5. Start Server
echo [INFO] Starting FastAPI server...
echo.
uvicorn app.main:app --reload

endlocal
