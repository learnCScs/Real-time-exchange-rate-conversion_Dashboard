@echo off
setlocal EnableDelayedExpansion
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
set "PYTHON_CMD=python"

:: Check local runtime
if exist "python_runtime\python.exe" (
    echo [INFO] Using local portable Python runtime.
    set "PYTHON_CMD=python_runtime\python.exe"
    goto install_deps
)

:: Check system python
python -c "import sys; exit(0) if sys.version_info >= (3, 8) else exit(1)" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] System Python 3.8+ detected.
    goto install_deps
)

:: Check py launcher
py -3 -c "import sys; exit(0) if sys.version_info >= (3, 8) else exit(1)" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Python 3.8+ detected via py launcher.
    set "PYTHON_CMD=py -3"
    goto install_deps
)

:: Download portable python
echo [WARN] No suitable Python 3.8+ found.
echo [INFO] Downloading Portable Python 3.10...
if not exist "python_runtime" mkdir "python_runtime"

echo   - Downloading zip...
powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip' -OutFile 'python_runtime\python.zip' }"
if not exist "python_runtime\python.zip" (
    echo [ERROR] Download failed. Please check internet connection.
    pause
    exit /b 1
)

echo   - Extracting...
powershell -Command "& { Expand-Archive -Path 'python_runtime\python.zip' -DestinationPath 'python_runtime' -Force }"
del "python_runtime\python.zip"

echo   - Configuring...
powershell -Command "& { $pth = Get-ChildItem 'python_runtime\*._pth'; $c = Get-Content $pth; $c | ForEach-Object { if ($_ -match '#import site') { 'import site' } else { $_ } } | Set-Content $pth }"

echo   - Installing pip...
powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'python_runtime\get-pip.py' }"
"python_runtime\python.exe" "python_runtime\get-pip.py" --no-warn-script-location
del "python_runtime\get-pip.py"

set "PYTHON_CMD=python_runtime\python.exe"

:install_deps
if not exist requirements.txt goto start_server
echo [INFO] Installing dependencies...
!PYTHON_CMD! -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    echo Please check your internet connection.
    pause
    exit /b 1
)

:start_server
echo [INFO] Opening browser...
start /b cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:8000"

echo [INFO] Starting FastAPI server...
echo.
!PYTHON_CMD! -m uvicorn app.main:app --reload

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
