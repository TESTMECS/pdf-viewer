from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

# Association table for many-to-many relationship between books and tags
book_tags = db.Table('book_tags',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Book(db.Model):
    """Model for books in the PDF viewer."""
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(500), unique=True, nullable=False)
    folder = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, nullable=True)
    
    # Relationship to tags - many-to-many
    tags = db.relationship('Tag', secondary=book_tags, backref=db.backref('books', lazy='dynamic'))

    def __init__(self, path, folder, filename):
        self.path = path
        self.folder = folder
        self.filename = filename

    def __repr__(self):
        return f'<Book {self.filename}>'
    
    def to_dict(self):
        """Convert book to dictionary."""
        return {
            'id': self.id,
            'path': self.path,
            'folder': self.folder,
            'filename': self.filename,
            'added_date': self.added_date.isoformat() if self.added_date else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'tags': [tag.name for tag in self.tags] # type: ignore
        }

class Tag(db.Model):
    """Model for tags that can be applied to books."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return f'<Tag {self.name}>'
    
    def to_dict(self):
        """Convert tag to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'book_count': self.books.count() # type: ignore
        }

# Database operation functions
def init_db(app):
    """Initialize the database and create tables."""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Add default tags if they don't exist
        default_tags = [
            {"name": "finished", "description": "Books you have finished reading"},
            {"name": "in_progress", "description": "Books you are currently reading"},
            {"name": "backlog", "description": "Books you plan to read in the future"}
        ]
        
        for tag_data in default_tags:
            if not Tag.query.filter_by(name=tag_data["name"]).first():
                tag = Tag(name=tag_data["name"], description=tag_data["description"])
                db.session.add(tag)
        
        db.session.commit()

def get_or_create_book(path, folder, filename):
    """Get a book from the database or create it if it doesn't exist."""
    book = Book.query.filter_by(path=path).first()
    if not book:
        book = Book(path=path, folder=folder, filename=filename)
        db.session.add(book)
        db.session.commit()
    return book

def get_or_create_tag(name, description=None):
    """Get a tag from the database or create it if it doesn't exist."""
    tag = Tag.query.filter_by(name=name).first()
    if not tag:
        tag = Tag(name=name, description=description)
        db.session.add(tag)
        db.session.commit()
    return tag

def add_tag_to_book(book_path, tag_name):
    """Add a tag to a book."""
    # Parse book path into folder and filename
    if '/' in book_path:
        folder, filename = os.path.split(book_path)
    else:
        folder = "root"
        filename = book_path
    
    book = get_or_create_book(book_path, folder, filename)
    tag = get_or_create_tag(tag_name)
    
    # Check if book already has this tag
    if tag not in book.tags: # type: ignore
        # If tag is a reading status, remove other reading status tags
        reading_statuses = ["finished", "in_progress", "backlog"]
        if tag_name in reading_statuses:
            for status in reading_statuses:
                if status != tag_name:
                    status_tag = Tag.query.filter_by(name=status).first()
                    if status_tag and status_tag in book.tags:
                        book.tags.remove(status_tag)
        
        # Add the new tag
        book.tags.append(tag)
        db.session.commit()
    
    return book

def remove_tag_from_book(book_path, tag_name):
    """Remove a tag from a book."""
    book = Book.query.filter_by(path=book_path).first()
    tag = Tag.query.filter_by(name=tag_name).first()
    
    if book and tag and tag in book.tags:
        book.tags.remove(tag)
        db.session.commit()
        return True
    
    return False

def get_books_by_tag(tag_name):
    """Get all books with a specific tag."""
    tag = Tag.query.filter_by(name=tag_name).first()
    if tag:
        return [book.path for book in tag.books]
    return []

def get_all_tags():
    """Get all available tags."""
    return Tag.query.all()

def get_book_tags(book_path):
    """Get all tags for a specific book."""
    book = Book.query.filter_by(path=book_path).first()
    if book:
        return [tag.name for tag in book.tags]
    return []

def get_tag_statistics():
    """Get statistics about tag usage."""
    tags = Tag.query.all()
    stats = {}
    
    for tag in tags:
        stats[tag.name] = {
            'count': tag.books.count(),
            'description': tag.description
        }
    
    return stats 