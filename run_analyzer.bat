@echo off
REM Log File Analyzer Batch Script
REM Quick launcher for Windows systems

echo Log File Analyzer - Quick Launcher
echo ===================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher
    pause
    exit /b 1
)

echo Python is available
echo.

:menu
echo Choose an option:
echo 1. Launch GUI Interface
echo 2. Analyze sample application log
echo 3. Analyze sample Apache access log
echo 4. Analyze sample system log
echo 5. Run comprehensive test
echo 6. View help information
echo 7. Exit
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" (
    echo Launching GUI...
    python log_analyzer.py --gui
    goto menu
)

if "%choice%"=="2" (
    echo Analyzing sample application log...
    python log_analyzer.py sample_logs\application.log
    echo.
    pause
    goto menu
)

if "%choice%"=="3" (
    echo Analyzing sample Apache access log...
    python log_analyzer.py sample_logs\apache_access.log
    echo.
    pause
    goto menu
)

if "%choice%"=="4" (
    echo Analyzing sample system log...
    python log_analyzer.py sample_logs\system.log
    echo.
    pause
    goto menu
)

if "%choice%"=="5" (
    echo Running comprehensive test...
    python test_analyzer.py
    echo.
    pause
    goto menu
)

if "%choice%"=="6" (
    echo Displaying help information...
    python log_analyzer.py --help
    echo.
    pause
    goto menu
)

if "%choice%"=="7" (
    echo Goodbye!
    exit /b 0
)

echo Invalid choice. Please try again.
echo.
goto menu
