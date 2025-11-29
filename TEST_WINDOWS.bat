@echo off
REM Test script for Windows
cls

echo ========================================================
echo.
echo           TESTING ADMIN PANEL
echo.
echo ========================================================
echo.

set PASS=0
set FAIL=0

REM Test 1: Python
echo [1/8] Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo    X FAIL
    set /a FAIL+=1
) else (
    python --version
    echo    - PASS
    set /a PASS+=1
)
echo.

REM Test 2: Dependencies
echo [2/8] Dependencies...
python -c "import flask, requests, psutil, speedtest" >nul 2>&1
if errorlevel 1 (
    echo    X FAIL - Some modules missing
    set /a FAIL+=1
) else (
    echo    - PASS - All modules available
    set /a PASS+=1
)
echo.

REM Test 3: admin_panel.py
echo [3/8] admin_panel.py exists...
if not exist "admin_panel.py" (
    echo    X FAIL
    set /a FAIL+=1
) else (
    echo    - PASS
    set /a PASS+=1
)
echo.

REM Test 4: Import
echo [4/8] Import admin_panel...
python -c "import admin_panel" >nul 2>&1
if errorlevel 1 (
    echo    X FAIL
    set /a FAIL+=1
) else (
    echo    - PASS
    set /a PASS+=1
)
echo.

REM Test 5: Templates
echo [5/8] Templates folder...
if not exist "templates" (
    echo    X FAIL
    set /a FAIL+=1
) else (
    dir /b templates\*.html | find /c /v "" > temp.txt
    set /p COUNT=<temp.txt
    del temp.txt
    echo    - PASS ^(%COUNT% files^)
    set /a PASS+=1
)
echo.

REM Test 6: Static files
echo [6/8] Static files...
if not exist "static\css\style.css" (
    echo    X FAIL - CSS missing
    set /a FAIL+=1
) else if not exist "static\js\main.js" (
    echo    X FAIL - JS missing
    set /a FAIL+=1
) else (
    echo    - PASS
    set /a PASS+=1
)
echo.

REM Test 7: Configuration
echo [7/8] Configuration...
if not exist ".env" (
    echo    ! WARNING - .env missing
    set /a FAIL+=1
) else (
    echo    - PASS
    set /a PASS+=1
)
echo.

REM Test 8: Flask routes
echo [8/8] Flask routes...
python -c "import admin_panel; print('Routes:', len(list(admin_panel.app.url_map.iter_rules())))" 2>nul
if errorlevel 1 (
    echo    X FAIL
    set /a FAIL+=1
) else (
    echo    - PASS
    set /a PASS+=1
)
echo.

echo ========================================================
echo.
echo  Results: %PASS% passed, %FAIL% failed
echo.
if %FAIL% EQU 0 (
    echo  - ALL TESTS PASSED!
    echo  - Ready to run: START_WINDOWS.bat
) else (
    echo  X SOME TESTS FAILED
    echo  - Check errors above
)
echo.
echo ========================================================
pause
