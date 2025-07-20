import os
from datetime import timedelta

# Get the base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class Config:
    """Base configuration class"""
    
    # Database configuration - Local SQLite
    DATABASE_PATH = os.path.join(BASE_DIR, 'neet_test.db')
    DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL query logging
    
    # Security configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-please-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-please-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Application configuration
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
    
    # CORS configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Pagination defaults
    QUESTIONS_PER_PAGE = 20
    TESTS_PER_PAGE = 10
    LEADERBOARD_SIZE = 10
    
    # Test configuration
    MAX_QUESTIONS_PER_TEST = 100
    MIN_QUESTIONS_PER_TEST = 1
    DEFAULT_TEST_TIME_LIMIT = 3600  # 1 hour in seconds
    
    # Rate limiting (if needed)
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Change to True if you want to see SQL queries

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_PATH = ':memory:'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # In production, you can still use SQLite or upgrade to PostgreSQL/MySQL
    DATABASE_PATH = os.path.join(BASE_DIR, 'neet_test_prod.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Current configuration - default to development
current_config = config.get(os.environ.get('FLASK_ENV', 'development'), DevelopmentConfig)

# Legacy support (for backward compatibility)
DATABASE_URI = current_config.SQLALCHEMY_DATABASE_URI
SECRET_KEY = current_config.SECRET_KEY
DEBUG = current_config.DEBUG
