# PDF Book Viewer

A lightweight web application for viewing and organizing your books.

## Features

- Simple web interface to browse and view your PDF collection
- Automatically organizes PDFs by folder structure
- Minimal setup required
- Mobile-friendly interface
- Tag books as "finished", "in progress", or "backlog"
- Create custom tags to organize your collection
- SQLite database for persistent storage

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Docker (optional, for containerized deployment)

### Installation

#### Option 1: Standard Installation

1. Clone this repository or download the files.

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Run the setup script to create the necessary directories and initialize the database:

   ```
   just start 
   ```
   or
   ```
   uv run app.py
   ```

5. Add your PDF books to the `books` directory. Alternatively, you can create a symbolic link to your existing PDF collection:

   ```
   # Linux/Mac
   ln -sf /path/to/your/pdf/collection books

   # Windows (requires administrator privileges)
   mklink /D books C:\path\to\your\pdf\collection
   ```

#### Option 2: Docker Installation

1. Clone this repository:

   ```
   git clone <repository-url>
   cd book_viewer
   ```

2. Build and run the Docker container:

   ```
   docker-compose up -d
   ```

3. To use your existing PDF collection with Docker, edit the `docker-compose.yml` file and modify the volume mapping:
   ```yaml
   volumes:
     - /path/to/your/pdfs:/app/books
     - ./data:/app/data
   ```

### Running the Application

#### Standard Method

1. Start the application using the provided scripts:

   **Linux/Mac**:

   ```bash
   ./run.sh
   ```

   **Windows**:

   ```
   run.bat
   ```

   These scripts will:

   - Ask you for environment variable configuration
   - Offer choices for database location (including temporary database options)
   - Create necessary directories with proper permissions
   - Check write permissions for the database directory
   - Set up a virtual environment if needed
   - Start the application

   Alternatively, you can start it manually:

   ```
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

#### Docker Method

1. After running `docker-compose up -d`, the application will be available at:

   ```
   http://localhost:5000
   ```

2. You can also use the maintenance script for common Docker operations:

   ```
   # Start the application
   ./scripts/maintenance.sh start

   # View logs
   ./scripts/maintenance.sh logs

   # Backup the database
   ./scripts/maintenance.sh backup

   # Get help on all commands
   ./scripts/maintenance.sh help
   ```

## Maintenance Tools

### Python Utility Script

For standard installations, the Python utility script helps manage the application:

```
# Set up the application (create directories and database)
python scripts/setup.py setup

# Backup the database
python scripts/setup.py backup

# Restore from a backup
python scripts/setup.py restore backups/books_20230101_120000.db

# Reset the database (removes all tags)
python scripts/setup.py reset

# Analyze PDF collection
python scripts/setup.py analyze
```

### Docker Maintenance Script

For Docker installations, use the maintenance script:

```
# Start the application
./scripts/maintenance.sh start

# Stop the application
./scripts/maintenance.sh stop

# View logs
./scripts/maintenance.sh logs

# Backup the database
./scripts/maintenance.sh backup

# Restore from a backup
./scripts/maintenance.sh restore backups/books_20230101_120000.db
```

## Environment Variables

The application can be configured using environment variables. When you run the startup scripts (`run.sh` or `run.bat`), you'll be prompted to configure these variables interactively.

### Available Environment Variables:

- `PDF_DIR`: Directory path for PDF files (default: `./books`)
- `DATABASE_PATH`: Path for SQLite database (default: `./data/books.db`)
- `APP_HOST`: Host to run the application on (default: `127.0.0.1`)
- `APP_PORT`: Port to run the application on (default: `5000`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `FLASK_ENV`: Application environment (default: `production`)

### Setting Environment Variables Manually:

If you prefer to set environment variables before running the application:

**Linux/Mac**:

```bash
export PDF_DIR=/custom/path/to/pdfs
export DATABASE_PATH=/custom/path/to/database.db
./run.sh
```

**Windows**:

```
set PDF_DIR=C:\custom\path\to\pdfs
set DATABASE_PATH=C:\custom\path\to\database.db
run.bat
```

### Database Location Options:

The startup scripts provide three options for database location:

1. **Default location** (`./data/books.db`): Uses the standard location in the data directory
2. **Temporary database**: Creates the database in the system's temporary directory
   - Linux/Mac: `/tmp/pdf_viewer_books.db`
   - Windows: `%TEMP%\pdf_viewer_books.db`
3. **Custom location**: Specify any path where you have write permissions

### Troubleshooting Database Access:

If you encounter database access errors:

1. The startup scripts will detect permission issues and offer to use a temporary database
2. You can manually set the `DATABASE_PATH` to a location where you have write permissions
3. Ensure that both the database directory and the parent directories have appropriate permissions

## Directory Structure

- `app.py` - The main Flask application
- `database.py` - Database models and operations
- `templates/` - Contains HTML templates
- `static/` - CSS and JavaScript files
- `books/` - Directory for PDF files (or symlink to your collection)
- `data/` - Database and other data storage
- `scripts/` - Maintenance and utility scripts
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker container configuration
- `docker-compose.yml` - Docker Compose configuration
- `run.sh` - Shell script to easily start the application (Linux/Mac)
- `run.bat` - Batch file to easily start the application (Windows)

## Tag Management

To manage your book collection:

1. Click the "Manage Tags" button at the top of the main page
2. On the tag management page, you can:
   - Create new custom tags
   - Edit existing tag names and descriptions
   - Delete tags that are no longer needed
   - See statistics about tag usage

From the main page, you can tag books by:

1. Clicking the "+ Add Tag" dropdown next to any book
2. Selecting a tag from the list
3. The tag will be applied instantly and saved to the database

## Database Management

The application uses SQLite for database storage. With Docker deployment, you can:

1. Backup the database:

   ```
   ./scripts/maintenance.sh backup
   ```

2. Restore from a backup:

   ```
   ./scripts/maintenance.sh restore backups/books_20230101_120000.db
   ```

3. Reset the database (warning: removes all tags):
   ```
   ./scripts/maintenance.sh reset-db
   ```

## Customization

You can customize the appearance by modifying the CSS in `static/css/style.css`.

## Environment Support

The application can run in different environments:

- **Development**: Set `FLASK_ENV=development` for debugging
- **Production**: Set `FLASK_ENV=production` for a production setup
- **Testing**: For automated testing scenarios

## License

This project is open source and available under the MIT License.
