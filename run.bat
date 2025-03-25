@echo off
REM PDF Book Viewer - Startup Script for Windows
REM This script starts the PDF Book Viewer application

echo  _____  _____  _____    _____                _      _    _ _                         
echo ^|  __ \^|  __ \^|  ___^|  ^|  __ \              ^| ^|    ^| ^|  ^| ^(^)                        
echo ^| ^|__^) ^| ^|  ^| ^| ^|__    ^| ^|__^) ^|___   ___  __^| ^| __ ^| ^|  ^| ^|_  _____      _____ _ __ 
echo ^|  ___/^| ^|  ^| ^|  __^|   ^|  _  // _ \ / _ \/ _  ^|/ / ^| ^|/\^| ^| ^|/ _ \ \ /\ / / _ \ '__^|
echo ^| ^|    ^| ^|__^| ^| ^|      ^| ^| \ \ ^(_^) ^|  __/ ^(_^| ^| ^|  \  /\  / ^|  __/\ V  V /  __/ ^|   
echo ^|_^|    ^|_____/^|_^|      ^|_^|  \_\___/ \___^|\__,_^|_^|   \/  \/^|_^|\___^| \_/\_/ \___^|_^|   
echo.
echo ------------------------------------------------------------------------
echo   PDF Book Viewer - A simple web application for viewing your PDFs
echo ------------------------------------------------------------------------
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in the PATH.
    echo Please install Python and try again.
    exit /b 1
)

REM Change to the script's directory
cd /d "%~dp0"

REM Prompt for environment variables
echo.
echo Configure environment variables (press Enter to accept defaults):

set /p FLASK_ENV_INPUT="Environment (production/development) [production]: "
if not "%FLASK_ENV_INPUT%"=="" (
    set FLASK_ENV=%FLASK_ENV_INPUT%
) else (
    set FLASK_ENV=production
)

set /p PDF_DIR_INPUT="PDF directory path [./books]: "
if not "%PDF_DIR_INPUT%"=="" (
    set PDF_DIR=%PDF_DIR_INPUT%
) else (
    set PDF_DIR=./books
)

set /p APP_HOST_INPUT="Host address to listen on [127.0.0.1]: "
if not "%APP_HOST_INPUT%"=="" (
    set APP_HOST=%APP_HOST_INPUT%
) else (
    set APP_HOST=127.0.0.1
)

set /p APP_PORT_INPUT="Port to listen on [5000]: "
if not "%APP_PORT_INPUT%"=="" (
    set APP_PORT=%APP_PORT_INPUT%
) else (
    set APP_PORT=5000
)

set /p LOG_LEVEL_INPUT="Logging level [INFO]: "
if not "%LOG_LEVEL_INPUT%"=="" (
    set LOG_LEVEL=%LOG_LEVEL_INPUT%
) else (
    set LOG_LEVEL=INFO
)

REM Prompt for database location options
echo.
echo Database Configuration:
echo 1) Use default location (./data/books.db)
echo 2) Use temporary database (%TEMP%\pdf_viewer_books.db)
echo 3) Specify custom location
set /p DB_OPTION="Select an option [1-3]: "

if "%DB_OPTION%"=="2" (
    set DATABASE_PATH=%TEMP%\pdf_viewer_books.db
    echo Using temporary database at: %DATABASE_PATH%
) else if "%DB_OPTION%"=="3" (
    set /p DATABASE_PATH_INPUT="Enter database path [./data/books.db]: "
    if not "%DATABASE_PATH_INPUT%"=="" (
        set DATABASE_PATH=%DATABASE_PATH_INPUT%
    ) else (
        set DATABASE_PATH=./data/books.db
    )
) else (
    set DATABASE_PATH=./data/books.db
    echo Using default database at: %DATABASE_PATH%
)

REM Extract the directory from DATABASE_PATH
for %%F in ("%DATABASE_PATH%") do set DB_DIR=%%~dpF

REM Remove trailing backslash if present
if "%DB_DIR:~-1%"=="\" set DB_DIR=%DB_DIR:~0,-1%

REM Create necessary directories with proper permissions
echo.
echo Setting up directories...

REM Create PDF directory if it doesn't exist
if not exist "%PDF_DIR%" (
    echo Creating PDF directory: %PDF_DIR%
    mkdir "%PDF_DIR%" 2>nul
    echo Please add your PDF files to the %PDF_DIR% directory.
)

REM Create database directory if it doesn't exist
if not exist "%DB_DIR%" (
    echo Creating database directory: %DB_DIR%
    mkdir "%DB_DIR%" 2>nul
)

REM Check if we can write to the database directory by trying to create a test file
echo Testing database directory permissions...
set TEST_FILE=%DB_DIR%\test_access.tmp
echo test > "%TEST_FILE%" 2>nul
if not exist "%TEST_FILE%" (
    echo Warning: Cannot write to database directory: %DB_DIR%
    echo Would you like to change to a temporary database location? (y/n)
    set /p USE_TEMP_DB=
    if /i "%USE_TEMP_DB%"=="y" (
        set DATABASE_PATH=%TEMP%\pdf_viewer_books.db
        echo Using temporary database at: %DATABASE_PATH%
    ) else (
        echo Error: Cannot proceed without a writable database location.
        exit /b 1
    )
) else (
    del "%TEST_FILE%"
)

REM Check if the virtual environment exists
if not exist .venv (
    if not exist venv (
        echo.
        echo No virtual environment found. Would you like to create one? (y/n)
        set /p create_venv=
        if /i "%create_venv%"=="y" (
            echo Creating virtual environment...
            python -m venv .venv
            
            if exist .venv (
                if exist .venv\Scripts\activate.bat (
                    call .venv\Scripts\activate.bat
                    
                    echo Installing dependencies...
                    pip install -r requirements.txt
                ) else (
                    echo Failed to find activation script. Continuing without virtual environment.
                )
            ) else (
                echo Failed to create virtual environment. Continuing without it.
            )
        )
    )
)

REM Activate virtual environment if it exists
if exist .venv (
    if exist .venv\Scripts\activate.bat (
        call .venv\Scripts\activate.bat
    )
) else if exist venv (
    if exist venv\Scripts\activate.bat (
        call venv\Scripts\activate.bat
    )
)

REM Print configuration
echo.
echo Configuration:
echo - FLASK_ENV: %FLASK_ENV%
echo - PDF_DIR: %PDF_DIR%
echo - DATABASE_PATH: %DATABASE_PATH%
echo - APP_HOST: %APP_HOST%
echo - APP_PORT: %APP_PORT%
echo - LOG_LEVEL: %LOG_LEVEL%
echo.

REM Run setup script to initialize the database if needed
echo Initializing database...
if exist scripts\setup.py (
    python scripts\setup.py setup
)

REM Start the application
echo.
echo Starting PDF Book Viewer...
echo Press Ctrl+C to stop the application.
echo.
python app.py

REM Exit with the exit code from the Python application
exit /b %ERRORLEVEL% 