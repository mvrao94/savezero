@echo off
title Instagram Saved Posts Cleanser
cd /d "%~dp0"
echo ========================================================
echo Starting Instagram Saved Cleanser in Foreground...
echo (Note: Please close any open Chrome automation windows)
echo ========================================================

set "PYTHON_CMD=.venv\Scripts\python.exe"
set "EXIT_CODE=0"
if exist "%PYTHON_CMD%" (
	"%PYTHON_CMD%" -c "import sys" >nul 2>&1
	if errorlevel 1 rmdir /s /q .venv
)
if not exist "%PYTHON_CMD%" (
	where py >nul 2>&1
	if errorlevel 1 (
		echo Error: Python Launcher is not installed or not in PATH.
		set "EXIT_CODE=1"
		goto finish
	)
	echo Creating project virtual environment...
	py -3 -m venv .venv
	if errorlevel 1 (
		echo Error: Could not create the project virtual environment.
		set "EXIT_CODE=1"
		goto finish
	)
)

"%PYTHON_CMD%" -c "import selenium, dotenv, webdriver_manager" >nul 2>&1
if errorlevel 1 (
	echo Installing SaveZero dependencies...
	"%PYTHON_CMD%" -m pip install --disable-pip-version-check -e .
	if errorlevel 1 (
		echo Error: Dependency installation failed.
		set "EXIT_CODE=1"
		goto finish
	)
)

"%PYTHON_CMD%" cleaner.py %*
set "EXIT_CODE=%ERRORLEVEL%"

:finish
echo.
echo Process finished.
pause
exit /b %EXIT_CODE%
