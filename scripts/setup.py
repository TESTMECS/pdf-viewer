#!/usr/bin/env python3
"""
PDF Book Viewer - Setup and Maintenance Script
This script helps users set up and maintain the PDF Book Viewer application
"""

import os
import sys
import shutil
import sqlite3
import argparse
import datetime
from pathlib import Path

# Define directory paths
BASE_DIR = Path(__file__).parent.parent
BOOKS_DIR = BASE_DIR / "books"
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"
DB_PATH = DATA_DIR / "books.db"

def setup_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(BOOKS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    print(f"✓ Created directory structure:")
    print(f"  - Books directory: {BOOKS_DIR}")
    print(f"  - Data directory: {DATA_DIR}")
    print(f"  - Backups directory: {BACKUP_DIR}")

def init_database():
    """Initialize the database (simple SQLite initialization)"""
    try:
        # Add parent directory to path so we can import app
        sys.path.append(str(BASE_DIR))
        
        # Import app and initialize database
        try:
            # Try to import database module
            from database import init_db as init_database_func
            init_database_func()
            print(f"✓ Database initialized at {DB_PATH}")
            return True
        except (ImportError, AttributeError):
            # If import fails, create a minimal empty database
            conn = sqlite3.connect(DB_PATH)
            conn.close()
            print(f"✓ Created empty database at {DB_PATH}")
            print("  Note: Database tables will be created when you run the application.")
            return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def backup_database():
    """Backup the database"""
    if not DB_PATH.exists():
        print("No database found to backup.")
        return
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"books_{timestamp}.db"
    
    try:
        shutil.copy2(DB_PATH, backup_file)
        print(f"✓ Database backed up to {backup_file}")
    except Exception as e:
        print(f"Error backing up database: {e}")

def restore_database(backup_file):
    """Restore the database from a backup"""
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        print(f"Error: Backup file not found: {backup_path}")
        return
        
    try:
        # Make a backup before restoring
        backup_database()
        
        # Restore from backup
        shutil.copy2(backup_path, DB_PATH)
        print(f"✓ Database restored from {backup_path}")
        print("  Note: Please restart the application for changes to take effect.")
    except Exception as e:
        print(f"Error restoring database: {e}")

def reset_database():
    """Reset the database"""
    try:
        # Make a backup before resetting
        backup_database()
        
        # Delete and recreate an empty database
        if DB_PATH.exists():
            os.remove(DB_PATH)
        
        # Create an empty database
        conn = sqlite3.connect(DB_PATH)
        conn.close()
        
        print("✓ Database has been reset.")
        print("  Note: Database tables will be created when you run the application.")
    except Exception as e:
        print(f"Error resetting database: {e}")

def analyze_pdfs():
    """Analyze PDFs in the books directory"""
    pdf_count = 0
    subdirs = set()
    
    for root, dirs, files in os.walk(BOOKS_DIR):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_count += 1
                rel_path = os.path.relpath(root, BOOKS_DIR)
                if rel_path != '.':
                    subdirs.add(rel_path)
    
    print(f"✓ Found {pdf_count} PDF files in {len(subdirs) + 1} directories")
    if pdf_count == 0:
        print(f"  You can add PDFs to the {BOOKS_DIR} directory.")
    else:
        print(f"  Directory structure:")
        print(f"  - {BOOKS_DIR}")
        for subdir in sorted(subdirs):
            print(f"    - {subdir}")

def main():
    parser = argparse.ArgumentParser(description="PDF Book Viewer Setup and Maintenance")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up the PDF Book Viewer")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup the database")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore the database from a backup")
    restore_parser.add_argument("file", help="Backup file to restore from")
    
    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset the database")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze PDFs in the books directory")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        print("Setting up PDF Book Viewer...")
        setup_directories()
        if init_database():
            print("\nSetup completed successfully!")
            print("You can now run 'python app.py' to start the application.")
        
    elif args.command == "backup":
        backup_database()
        
    elif args.command == "restore":
        restore_database(args.file)
        
    elif args.command == "reset":
        print("Warning: This will delete all tags and book information.")
        response = input("Are you sure you want to reset the database? (y/n): ")
        if response.lower() == "y":
            reset_database()
        else:
            print("Reset cancelled.")
            
    elif args.command == "analyze":
        analyze_pdfs()
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 