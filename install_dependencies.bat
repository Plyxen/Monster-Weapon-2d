@echo off
REM Monster-Weapon-2D Dependency Installer
REM This script installs all required Python dependencies for the game

echo ========================================
echo Monster-Weapon-2D Dependency Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo Python detected:
python --version
echo.

REM Check if pip is available
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    echo.
    pause
    exit /b 1
)

echo pip detected:
python -m pip --version
echo.

REM Upgrade pip to latest version
echo Upgrading pip to latest version...
python -m pip install --upgrade pip
echo.

REM Install dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
echo.
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check the error messages above
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo You can now run the game using play.bat
echo.
pause
