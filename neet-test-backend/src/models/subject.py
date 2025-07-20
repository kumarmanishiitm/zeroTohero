from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean
from database.connection import db

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    def __init__(self, name, description=None, is_active=True):
        self.name = name
        self.description = description
        self.is_active = is_active

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active
        }

    def get_topics(self):
        """Get all active topics for this subject"""
        from models.topic import Topic
        topics = Topic.query.filter_by(subject_id=self.id, is_active=True).all()
        return [topic.to_dict() for topic in topics]

    def __repr__(self):
        return f"<Subject(id={self.id}, name='{self.name}')>"

# Pre-defined subjects for NEET
NEET_SUBJECTS = [
    {"name": "Physics", "description": "Study of matter, energy, and their interactions"},
    {"name": "Chemistry", "description": "Study of substances, their properties, composition, and reactions"},
    {"name": "Biology", "description": "Study of living organisms and their processes"}
]