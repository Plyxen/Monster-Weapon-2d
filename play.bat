@echo off
echo ============================================
echo   MONSTER WEAPON 2D - ROGUELIKE DUNGEON
echo ============================================
echo.
echo Checking dependencies...

REM Check if pygame is installed
python -c "import pygame" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [!] Dependencies missing! Installing requirements...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Failed to install dependencies!
        echo Please install Python and pip first.
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependencies installed successfully!
    echo.
)

echo [OK] Starting game...
echo.
python GameLoader.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Game failed to start!
    pause
)
exit
