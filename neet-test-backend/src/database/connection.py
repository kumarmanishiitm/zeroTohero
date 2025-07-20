import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from flask_sqlalchemy import SQLAlchemy

# Create local database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'neet_test.db')
DATABASE_URI = f'sqlite:///{DB_PATH}'

# Create declarative base for models
Base = declarative_base()

# SQLAlchemy database instance
db = SQLAlchemy()

# Create a new SQLAlchemy engine instance
engine = create_engine(DATABASE_URI, echo=False)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
def get_session():
    return Session()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)