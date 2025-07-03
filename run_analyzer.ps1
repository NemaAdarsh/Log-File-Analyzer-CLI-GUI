# Log File Analyzer PowerShell Launcher
# Professional launcher script for Windows PowerShell

param(
    [string]$LogFile = "",
    [switch]$GUI = $false,
    [switch]$Test = $false,
    [switch]$Help = $false
)

Write-Host "Log File Analyzer - PowerShell Launcher" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python detected: $pythonVersion" -ForegroundColor Cyan
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.6 or higher" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Handle command line parameters
if ($Help) {
    Write-Host "Displaying help information..." -ForegroundColor Yellow
    python log_analyzer.py --help
    exit 0
}

if ($Test) {
    Write-Host "Running comprehensive test suite..." -ForegroundColor Yellow
    python test_analyzer.py
    exit 0
}

if ($GUI) {
    Write-Host "Launching GUI interface..." -ForegroundColor Yellow
    python log_analyzer.py --gui
    exit 0
}

if ($LogFile -ne "") {
    if (Test-Path $LogFile) {
        Write-Host "Analyzing log file: $LogFile" -ForegroundColor Yellow
        python log_analyzer.py $LogFile
        exit 0
    } else {
        Write-Host "Error: Log file not found: $LogFile" -ForegroundColor Red
        exit 1
    }
}

# Interactive menu
do {
    Write-Host "Choose an option:" -ForegroundColor Cyan
    Write-Host "1. Launch GUI Interface" -ForegroundColor White
    Write-Host "2. Analyze sample application log" -ForegroundColor White
    Write-Host "3. Analyze sample Apache access log" -ForegroundColor White
    Write-Host "4. Analyze sample system log" -ForegroundColor White
    Write-Host "5. Run comprehensive test" -ForegroundColor White
    Write-Host "6. View help information" -ForegroundColor White
    Write-Host "7. Exit" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Enter your choice (1-7)"
    
    switch ($choice) {
        "1" {
            Write-Host "Launching GUI..." -ForegroundColor Yellow
            python log_analyzer.py --gui
        }
        "2" {
            Write-Host "Analyzing sample application log..." -ForegroundColor Yellow
            if (Test-Path "sample_logs\application.log") {
                python log_analyzer.py sample_logs\application.log
                Read-Host "Press Enter to continue"
            } else {
                Write-Host "Sample file not found. Please ensure sample_logs directory exists." -ForegroundColor Red
            }
        }
        "3" {
            Write-Host "Analyzing sample Apache access log..." -ForegroundColor Yellow
            if (Test-Path "sample_logs\apache_access.log") {
                python log_analyzer.py sample_logs\apache_access.log
                Read-Host "Press Enter to continue"
            } else {
                Write-Host "Sample file not found. Please ensure sample_logs directory exists." -ForegroundColor Red
            }
        }
        "4" {
            Write-Host "Analyzing sample system log..." -ForegroundColor Yellow
            if (Test-Path "sample_logs\system.log") {
                python log_analyzer.py sample_logs\system.log
                Read-Host "Press Enter to continue"
            } else {
                Write-Host "Sample file not found. Please ensure sample_logs directory exists." -ForegroundColor Red
            }
        }
        "5" {
            Write-Host "Running comprehensive test..." -ForegroundColor Yellow
            python test_analyzer.py
            Read-Host "Press Enter to continue"
        }
        "6" {
            Write-Host "Displaying help information..." -ForegroundColor Yellow
            python log_analyzer.py --help
            Read-Host "Press Enter to continue"
        }
        "7" {
            Write-Host "Goodbye!" -ForegroundColor Green
            exit 0
        }
        default {
            Write-Host "Invalid choice. Please try again." -ForegroundColor Red
        }
    }
    
    Write-Host ""
} while ($true)
