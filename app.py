from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for  # pip install flask
import os
import logging
import json
from database import db, init_db, Book, Tag
from database import add_tag_to_book, remove_tag_from_book, get_books_by_tag
from database import get_book_tags, get_all_tags, get_tag_statistics
from database import get_or_create_tag

app = Flask(__name__, static_folder='static')

# Get configuration from environment variables or use defaults
BOOKS_DIR = os.environ.get('PDF_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), "books"))
DB_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "books.db"))
APP_HOST = os.environ.get('APP_HOST', '0.0.0.0')
APP_PORT = int(os.environ.get('APP_PORT', 5000))

# Configure app
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

# Available tags (for easy reference)
AVAILABLE_TAGS = ["finished", "in_progress", "backlog"]

def get_books_structure():
    """Scan the books directory and return a dictionary of folders and their PDF files."""
    structure = {}
    try:
        for root, dirs, files in os.walk(BOOKS_DIR):
            folder = os.path.relpath(root, BOOKS_DIR)
            if folder == ".":
                folder = "root"
            structure[folder] = [f for f in files if f.lower().endswith(".pdf")]
    except Exception as e:
        logger.error(f"Error scanning books directory: {e}")
        structure = {"root": []}
    return structure

def get_book_path(folder, filename):
    """Create a unique identifier for a book based on its path."""
    if folder == "root":
        return filename
    return f"{folder}/{filename}"

@app.route("/")
def index():
    """Render the main page with the books structure."""
    books = get_books_structure()
    
    # Create a dictionary of book paths to their tags
    book_tags = {}
    
    # Get all books with their tags from the database
    with app.app_context():
        # For each book in the structure, find its tags
        for folder, files in books.items():
            for filename in files:
                book_path = get_book_path(folder, filename)
                tags = get_book_tags(book_path)
                if tags:
                    book_tags[book_path] = tags
    
    # Get all available tags for the UI
    available_tags = [tag.name for tag in get_all_tags()]
    
    return render_template("index.html", books=books, book_tags=book_tags, available_tags=available_tags)

@app.route("/books/<path:filepath>")
def serve_pdf(filepath):
    """Serve PDF files from the books directory."""
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    if directory:
        pdf_path = os.path.join(BOOKS_DIR, directory)
    else:
        pdf_path = BOOKS_DIR
    return send_from_directory(pdf_path, filename)

@app.route("/api/tags", methods=["POST"])
def update_tag():
    """Update tags for a book."""
    data = request.json
    if data is not None:
        book_path = data.get("book_path")
        tag = data.get("tag")
        action = data.get("action", "add")  # "add" or "remove"
    
    if not book_path or not tag or tag not in AVAILABLE_TAGS:
        return jsonify({"success": False, "error": "Invalid parameters"}), 400
    
    try:
        if action == "add":
            add_tag_to_book(book_path, tag)
            success = True
        else:  # remove
            success = remove_tag_from_book(book_path, tag)
        
        return jsonify({"success": success})
    except Exception as e:
        logger.error(f"Error updating tag: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/filter/<tag>")
def filter_by_tag(tag):
    """Show only books with the specified tag."""
    if tag not in AVAILABLE_TAGS and tag != "all":
        return redirect(url_for("index"))
    
    books = get_books_structure()
    
    # Create a dictionary of book paths to their tags
    book_tags = {}
    
    # Get all books with their tags from the database
    with app.app_context():
        # For each book in the structure, find its tags
        for folder, files in books.items():
            for filename in files:
                book_path = get_book_path(folder, filename)
                tags = get_book_tags(book_path)
                if tags:
                    book_tags[book_path] = tags
    
    # If filtering, create a filtered version of books
    if tag != "all":
        tagged_books = get_books_by_tag(tag)
        filtered_books = {}
        
        for folder, files in books.items():
            filtered_files = []
            for file in files:
                book_path = get_book_path(folder, file)
                if book_path in tagged_books:
                    filtered_files.append(file)
            if filtered_files:
                filtered_books[folder] = filtered_files
        books = filtered_books
    
    # Get all available tags for the UI
    available_tags = [tag.name for tag in get_all_tags()]
    
    return render_template("index.html", books=books, book_tags=book_tags, available_tags=available_tags, active_filter=tag)

# Tag Management Routes
@app.route("/tags")
def manage_tags():
    """Render the tag management page."""
    tags = [tag.to_dict() for tag in get_all_tags()]
    return render_template("tags.html", tags=tags)

@app.route("/api/tags/stats")
def get_tags_stats():
    """Get statistics about tag usage."""
    try:
        stats = get_tag_statistics()
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        logger.error(f"Error getting tag statistics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/tags/create", methods=["POST"])
def create_tag():
    """Create a new tag."""
    data = request.json
    if data is not None:
        name = data.get("name")
        description = data.get("description", "")
    
    if not name:
        return jsonify({"success": False, "error": "Tag name is required"}), 400
    
    try:
        tag = get_or_create_tag(name, description)
        return jsonify({"success": True, "tag": tag.to_dict()})
    except Exception as e:
        logger.error(f"Error creating tag: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/tags/update/<int:tag_id>", methods=["PUT"])
def update_tag_details(tag_id):
    """Update a tag's details."""
    data = request.json
    if data is not None:
        name = data.get("name")
        description = data.get("description", "")
    
    if not name:
        return jsonify({"success": False, "error": "Tag name is required"}), 400
    
    try:
        with app.app_context():
            tag = Tag.query.get(tag_id)
            if not tag:
                return jsonify({"success": False, "error": "Tag not found"}), 404
            
            # Prevent updating default tags
            if tag.name in AVAILABLE_TAGS and name != tag.name:
                return jsonify({"success": False, "error": "Cannot change name of default tags"}), 400
            
            tag.name = name
            tag.description = description
            db.session.commit()
            
            return jsonify({"success": True, "tag": tag.to_dict()})
    except Exception as e:
        logger.error(f"Error updating tag: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/tags/delete/<int:tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    """Delete a tag."""
    try:
        with app.app_context():
            tag = Tag.query.get(tag_id)
            if not tag:
                return jsonify({"success": False, "error": "Tag not found"}), 404
            
            # Prevent deleting default tags
            if tag.name in AVAILABLE_TAGS:
                return jsonify({"success": False, "error": "Cannot delete default tags"}), 400
            
            # Remove tag from all books
            for book in tag.books:
                book.tags.remove(tag)
            
            db.session.delete(tag)
            db.session.commit()
            
            return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error deleting tag: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Environment configuration
def configure_app_for_environment():
    """Configure the app based on the environment (dev, test, prod)."""
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        logging.getLogger().setLevel(logging.WARNING)
    elif env == 'testing':
        app.config['DEBUG'] = False
        app.config['TESTING'] = True
    else:  # development
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
    
    logger.info(f"Running in {env} environment")
    return env

if __name__ == "__main__":
    # Check if books directory exists
    if not os.path.exists(BOOKS_DIR):
        logger.warning(f"Books directory not found at {BOOKS_DIR}. Creating empty directory.")
        os.makedirs(BOOKS_DIR, exist_ok=True)
    
    # Ensure the data directory exists
    data_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    # Initialize the database
    init_db(app)
    
    # Configure environment
    env = configure_app_for_environment()
    
    # Output info about the app
    logger.info(f"Books directory: {BOOKS_DIR}")
    logger.info(f"Database path: {DB_PATH}")
    logger.info("Starting PDF Book Viewer...")
    
    # Run the Flask app
    app.run(debug=(env != 'production'), host=APP_HOST, port=APP_PORT) 