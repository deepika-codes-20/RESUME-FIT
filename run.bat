@echo off
title ResumeFit - ATS Resume Analyzer
echo ========================================================
echo        ResumeFit - ATS Resume Analyzer Launcher
echo ========================================================
echo.

:: Check for python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your PATH.
    echo Please install Python 3.8+ and ensure it is added to your PATH.
    pause
    exit /b 1
)

echo [1/2] Installing / Verifying required dependencies...
python -m pip install -r requirements.txt --quiet

echo.
echo [2/2] Starting ResumeFit Web Application...
echo.
echo ========================================================
echo  Application is running at: http://127.0.0.1:5000
echo  Open your web browser and navigate to the address above.
echo  Press Ctrl+C in this terminal to stop the server.
echo ========================================================
echo.

start http://127.0.0.1:5000
python app.py

pause
