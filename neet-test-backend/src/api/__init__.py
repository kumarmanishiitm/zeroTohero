# File: /neet-test-backend/neet-test-backend/src/api/__init__.py

from flask import Blueprint

api = Blueprint('api', __name__)

from .routes import *  # Import all routes to register them with the blueprint