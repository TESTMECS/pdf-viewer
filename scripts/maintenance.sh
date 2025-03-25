#!/bin/bash

# PDF Book Viewer - Maintenance Script
# This script provides utilities for managing the PDF Book Viewer application

set -e

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to display help information
show_help() {
    echo "PDF Book Viewer - Maintenance Script"
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start             Start the PDF Book Viewer container"
    echo "  stop              Stop the PDF Book Viewer container"
    echo "  restart           Restart the PDF Book Viewer container"
    echo "  status            Check the status of the PDF Book Viewer container"
    echo "  logs              View container logs"
    echo "  update            Pull latest changes and rebuild the container"
    echo "  backup            Backup the database to the backups directory"
    echo "  restore FILENAME  Restore the database from a backup file"
    echo "  reset-db          Reset the database (warning: removes all tags)"
    echo "  shell             Open a shell in the container"
    echo "  help              Show this help message"
}

# Function to backup the database
backup_database() {
    timestamp=$(date +"%Y%m%d_%H%M%S")
    mkdir -p backups
    echo "Creating backup of the database..."
    docker cp pdf-book-viewer:/app/data/books.db "./backups/books_${timestamp}.db"
    echo "Backup created: ./backups/books_${timestamp}.db"
}

# Function to restore the database
restore_database() {
    if [ -z "$1" ]; then
        echo "Error: Backup file not specified."
        echo "Usage: $0 restore FILENAME"
        return 1
    fi

    if [ ! -f "$1" ]; then
        echo "Error: Backup file not found: $1"
        return 1
    fi

    echo "Restoring database from backup: $1"
    docker cp "$1" pdf-book-viewer:/app/data/books.db
    echo "Database restored. Restarting container..."
    docker-compose restart
}

# Function to reset the database
reset_database() {
    echo "Warning: This will delete all tags and book information."
    read -p "Are you sure you want to reset the database? (y/n): " answer
    if [ "$answer" != "y" ]; then
        echo "Operation canceled."
        return 0
    fi

    echo "Making a backup before reset..."
    backup_database

    echo "Resetting database..."
    docker exec pdf-book-viewer rm -f /app/data/books.db
    docker-compose restart
    echo "Database has been reset."
}

# Main script logic
case "$1" in
    start)
        echo "Starting PDF Book Viewer..."
        docker-compose up -d
        ;;
    stop)
        echo "Stopping PDF Book Viewer..."
        docker-compose down
        ;;
    restart)
        echo "Restarting PDF Book Viewer..."
        docker-compose restart
        ;;
    status)
        echo "Checking container status..."
        docker-compose ps
        ;;
    logs)
        docker-compose logs -f
        ;;
    update)
        echo "Updating PDF Book Viewer..."
        git pull
        docker-compose down
        docker-compose build
        docker-compose up -d
        echo "Update completed."
        ;;
    backup)
        backup_database
        ;;
    restore)
        restore_database "$2"
        ;;
    reset-db)
        reset_database
        ;;
    shell)
        echo "Opening shell in container..."
        docker exec -it pdf-book-viewer /bin/bash
        ;;
    help|*)
        show_help
        ;;
esac

exit 0 