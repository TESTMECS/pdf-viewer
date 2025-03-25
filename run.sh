#!/bin/bash

# PDF Book Viewer - Startup Script
# This script starts the PDF Book Viewer application

# Define the banner function
show_banner() {
    echo " _____  _____  _____    _____                _      _    _ _                         "
    echo "|  __ \|  __ \|  ___|  |  __ \              | |    | |  | (_)                        "
    echo "| |__) | |  | | |__    | |__) |___   ___  __| | __ | |  | |_  _____      _____ _ __ "
    echo "|  ___/| |  | |  __|   |  _  // _ \ / _ \/ _  |/ / | |/\| | |/ _ \ \ /\ / / _ \ '__|"
    echo "| |    | |__| | |      | | \ \ (_) |  __/ (_| | |  \  /\  / |  __/\ V  V /  __/ |   "
    echo "|_|    |_____/|_|      |_|  \_\___/ \___|\__,_|_|   \/  \/|_|\___| \_/\_/ \___|_|   "
    echo "                                                                                    "
    echo "------------------------------------------------------------------------"
    echo "  PDF Book Viewer - A simple web application for viewing your PDFs"
    echo "------------------------------------------------------------------------"
}

# Show the banner
show_banner

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in the PATH."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Prompt for environment variables
read_env_var() {
    local var_name=$1
    local default_val=$2
    local description=$3
    local current_val=${!var_name}
    
    # Use current value if set, otherwise use default
    current_val=${current_val:-$default_val}
    
    # Prompt user for value
    echo -n "$description [$current_val]: "
    read user_input
    
    # If user didn't enter anything, use the current/default value
    if [ -z "$user_input" ]; then
        export "$var_name"="$current_val"
    else
        export "$var_name"="$user_input"
    fi
}

echo ""
echo "Configure environment variables (press Enter to accept defaults):"
read_env_var "FLASK_ENV" "production" "Environment (production/development)"
read_env_var "PDF_DIR" "./books" "PDF directory path"
read_env_var "APP_HOST" "127.0.0.1" "Host address to listen on"
read_env_var "APP_PORT" "5000" "Port to listen on"
read_env_var "LOG_LEVEL" "INFO" "Logging level"

# Prompt for database location with better options
echo ""
echo "Database Configuration:"
echo "1) Use default location (./data/books.db)"
echo "2) Use temporary database (/tmp/pdf_viewer_books.db)"
echo "3) Specify custom location"
echo -n "Select an option [1-3]: "
read db_option

case $db_option in
    2)
        export DATABASE_PATH="/tmp/pdf_viewer_books.db"
        echo "Using temporary database at: $DATABASE_PATH"
        ;;
    3)
        read_env_var "DATABASE_PATH" "./data/books.db" "Enter database path"
        ;;
    *)
        export DATABASE_PATH="./data/books.db"
        echo "Using default database at: $DATABASE_PATH"
        ;;
esac

# Extract the directory from DATABASE_PATH
DB_DIR=$(dirname "$DATABASE_PATH")

# Create necessary directories with proper permissions
echo ""
echo "Setting up directories..."

# Create PDF directory if it doesn't exist
if [ ! -d "$PDF_DIR" ]; then
    echo "Creating PDF directory: $PDF_DIR"
    mkdir -p "$PDF_DIR"
    chmod 755 "$PDF_DIR"
    echo "Please add your PDF files to the $PDF_DIR directory."
fi

# Create database directory if it doesn't exist
if [ ! -d "$DB_DIR" ]; then
    echo "Creating database directory: $DB_DIR"
    mkdir -p "$DB_DIR"
    chmod 755 "$DB_DIR"
fi

# Check if we can write to the database directory
if [ ! -w "$DB_DIR" ]; then
    echo "Warning: Cannot write to database directory: $DB_DIR"
    echo "Would you like to change to a temporary database location? (y/n)"
    read use_temp_db
    if [ "$use_temp_db" = "y" ]; then
        export DATABASE_PATH="/tmp/pdf_viewer_books.db"
        echo "Using temporary database at: $DATABASE_PATH"
    else
        echo "Error: Cannot proceed without a writable database location."
        exit 1
    fi
fi

# Check if the virtual environment exists
if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
    echo ""
    echo "No virtual environment found. Would you like to create one? (y/n)"
    read -r create_venv
    if [ "$create_venv" = "y" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
        
        if [ -d ".venv" ]; then
            if [ -f ".venv/bin/activate" ]; then
                source .venv/bin/activate
            elif [ -f ".venv/Scripts/activate" ]; then
                source .venv/Scripts/activate
            fi
            
            echo "Installing dependencies..."
            pip install -r requirements.txt
        else
            echo "Failed to create virtual environment. Continuing without it."
        fi
    fi
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    elif [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    fi
elif [ -d "venv" ]; then
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    fi
fi

# Print configuration
echo ""
echo "Configuration:"
echo "- FLASK_ENV: $FLASK_ENV"
echo "- PDF_DIR: $PDF_DIR"
echo "- DATABASE_PATH: $DATABASE_PATH"
echo "- APP_HOST: $APP_HOST"
echo "- APP_PORT: $APP_PORT"
echo "- LOG_LEVEL: $LOG_LEVEL"
echo ""

# Run setup script to initialize the database if needed
echo "Initializing database..."
if [ -f "scripts/setup.py" ]; then
    python scripts/setup.py setup
fi

# Start the application
echo ""
echo "Starting PDF Book Viewer..."
echo "Press Ctrl+C to stop the application."
echo ""
python app.py

# Exit with the exit code from the Python application
exit $? 