@echo off
REM Quick setup script for email automation
REM Installs all required dependencies

echo.
echo ============================================
echo  EMAIL AUTOMATION SETUP
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Install from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Installing Selenium...
pip install selenium
if errorlevel 1 (
    echo ERROR: Failed to install Selenium
    pause
    exit /b 1
)

echo [2/3] Installing GeckoDriver (Firefox WebDriver)...
pip install geckodriver-autoinstaller
if errorlevel 1 (
    echo WARNING: GeckoDriver auto-install failed
    echo Please download manually from:
    echo https://github.com/mozilla/geckodriver/releases
    echo Extract to: C:\webdrivers\geckodriver.exe
)

echo.
echo [3/3] Verifying Tor Browser...
if exist "C:\Program Files\Tor Browser\Browser\firefox.exe" (
    echo     ✓ Tor Browser found
) else (
    echo     ⚠ Tor Browser NOT found
    echo     Download from: https://www.torproject.org/download
)

echo.
echo ============================================
echo  ✅ SETUP COMPLETE!
echo ============================================
echo.
echo Next steps:
echo   1. Run: python run_complete_automation.py
echo   2. Follow the prompts
echo   3. Solve CAPTCHAs when asked
echo.
pause
