@echo off
REM Admin Panel Start Script for Windows
cls

echo ========================================================
echo.
echo           VPN VIETNAM - ADMIN PANEL
echo           Starting on Windows...
echo.
echo ========================================================
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo    X Python not found! Install Python 3.8+ from python.org
    pause
    exit /b 1
)
python --version
echo    - OK
echo.

REM Check dependencies
echo [2/5] Checking dependencies...
python -c "import flask, requests, psutil" >nul 2>&1
if errorlevel 1 (
    echo    ! Dependencies missing. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo    X Installation failed!
        pause
        exit /b 1
    )
)
echo    - OK
echo.

REM Check files
echo [3/5] Checking files...
if not exist "admin_panel.py" (
    echo    X admin_panel.py not found!
    pause
    exit /b 1
)
if not exist "templates" (
    echo    X templates folder not found!
    pause
    exit /b 1
)
echo    - OK
echo.

REM Check .env
echo [4/5] Checking configuration...
if not exist ".env" (
    echo    ! Creating .env from template...
    copy .env.example .env >nul
)
echo    - OK
echo.

REM Get IP
echo [5/5] Getting server information...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a
set IP=%IP:~1%
echo    - Local IP: %IP%
echo.

echo ========================================================
echo.
echo  Server will be available at:
echo.
echo    Local:   http://localhost:5000
echo    Network: http://%IP%:5000
echo.
echo  Login:
echo    Email:    admin@vpnvietnam.com
echo    Password: Vpnvietnam123@!
echo.
echo ========================================================
echo.
echo  IMPORTANT - If blank page appears:
echo.
echo    1. Clear browser cache (Ctrl+Shift+Delete)
echo    2. Use Incognito mode (Ctrl+Shift+N)
echo    3. Check URL: http://localhost:5000
echo.
echo ========================================================
echo.
echo  Starting server...
echo.
echo  Press Ctrl+C to stop
echo.
echo ========================================================
echo.

REM Start server
python admin_panel.py

echo.
echo ========================================================
echo  Server stopped
echo ========================================================
pause
