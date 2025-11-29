@echo off
REM Installation script for Windows
cls

echo ========================================================
echo.
echo     VPN VIETNAM - ADMIN PANEL
echo     Installation for Windows
echo.
echo ========================================================
echo.

REM Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo    X Python not found!
    echo.
    echo    Please install Python 3.8+ from:
    echo    https://www.python.org/downloads/
    echo.
    echo    Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
python --version
echo    - Python found
echo.

REM Check pip
echo [2/4] Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo    X pip not found!
    echo.
    echo    Installing pip...
    python -m ensurepip --upgrade
)
pip --version
echo    - pip ready
echo.

REM Install dependencies
echo [3/4] Installing dependencies...
echo    This may take a few minutes...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo    X Installation failed!
    echo    Try running as Administrator
    pause
    exit /b 1
)
echo.
echo    - Dependencies installed
echo.

REM Create .env
echo [4/4] Creating configuration...
if not exist ".env" (
    copy .env.example .env >nul
    echo    - .env created
) else (
    echo    - .env already exists
)
echo.

echo ========================================================
echo.
echo  Installation Complete!
echo.
echo  To start the server, run:
echo    START_WINDOWS.bat
echo.
echo ========================================================
pause
