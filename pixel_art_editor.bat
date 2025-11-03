@echo off
echo ============================================
echo   PIXEL ART EDITOR - MONSTER WEAPON 2D
echo ============================================
echo.
echo Launching Pixel Art Editor...
echo - 32 colors available for detailed pixel art
echo - Compact layout optimized for screen space
echo - Professional loading experience
echo.
python pixel_art_editor.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Editor failed to start!
    pause
)
