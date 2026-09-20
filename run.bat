@echo off
title Instagram Saved Posts Cleanser
cd /d "%~dp0"
echo ========================================================
echo Starting Instagram Saved Cleanser in Foreground...
echo (Note: Please close any open Chrome automation windows)
echo ========================================================
python cleaner.py %*
set "EXIT_CODE=%ERRORLEVEL%"
echo.
echo Process finished.
pause
exit /b %EXIT_CODE%
