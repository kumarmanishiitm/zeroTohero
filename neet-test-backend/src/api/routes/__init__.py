# File: /neet-test-backend/neet-test-backend/src/api/routes/__init__.py

from .subjects import subjects_bp
from .topics import topics_bp
from .questions import questions_bp
from .tests import tests_bp

__all__ = ['subjects_bp', 'topics_bp', 'questions_bp', 'tests_bp']