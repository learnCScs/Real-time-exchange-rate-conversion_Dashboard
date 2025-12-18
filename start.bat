@echo off
setlocal
title Exchange Rate Dashboard Launcher

echo ===================================================
echo      Exchange Rate Dashboard - One-Click Start
echo ===================================================
echo.

:: 1. Check for .env file
if exist .env goto check_python
echo [ERROR] .env file not found!
echo ---------------------------------------------------
echo Please rename '.env.example' to '.env' and configure
echo your API keys before running this script.
echo ---------------------------------------------------
pause
exit /b 1

:check_python
:: 2. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% equ 0 goto install_deps
echo [ERROR] Python is not installed or not in PATH.
echo Please install Python and add it to your PATH.
pause
exit /b 1

:install_deps
:: 3. Check/Install dependencies
if not exist requirements.txt goto start_server
echo [INFO] Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% equ 0 goto start_server
echo [ERROR] Failed to install dependencies.
echo Please check your internet connection or python environment.
pause
exit /b 1

:start_server
:: 4. Open Browser (Async)
echo [INFO] Opening browser...
start /b cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:8000"

:: 5. Start Server
echo [INFO] Starting FastAPI server...
echo.
python -m uvicorn app.main:app --reload

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server stopped unexpectedly.
    echo Possible reasons:
    echo  - Port 8000 is occupied.
    echo  - Missing dependencies.
    echo  - Code error.
    pause
)

echo.
echo [INFO] Server stopped.
pause
