@echo off
title Instagram Saved Posts Cleanser
cd /d "%~dp0"
echo ========================================================
echo Starting Instagram Saved Cleanser in Foreground...
echo (Note: Please close any open Chrome automation windows)
echo ========================================================
taskkill /f /im chromedriver.exe >nul 2>&1
python cleaner.py %*
echo.
echo Process finished.
pause
