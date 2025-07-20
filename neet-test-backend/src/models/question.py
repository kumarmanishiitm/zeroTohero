from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from database.connection import db
import enum

class DifficultyLevel(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)  # A, B, C, or D
    explanation = Column(Text, nullable=False)
    difficulty_level = Column(String(20), default='medium')
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    source = Column(String(50), default='manual', nullable=True)  # Track question source

    def __init__(self, question_text, option_a, option_b, option_c, option_d, 
                 correct_answer, explanation, subject_id, topic_id, difficulty_level='medium', is_active=True, difficulty=None, source='manual'):
        self.question_text = question_text
        self.option_a = option_a
        self.option_b = option_b
        self.option_c = option_c
        self.option_d = option_d
        self.correct_answer = correct_answer.upper() if correct_answer else 'A'  # Handle None values
        self.explanation = explanation
        self.subject_id = subject_id
        self.topic_id = topic_id
        self.is_active = is_active
        self.source = source
        
        # Handle both old enum style and new string style
        if difficulty:
            if isinstance(difficulty, DifficultyLevel):
                self.difficulty_level = difficulty.value
            else:
                self.difficulty_level = str(difficulty).lower()
        else:
            self.difficulty_level = difficulty_level

    def get_options(self):
        return {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d
        }

    @property
    def difficulty(self):
        """Backward compatibility property for old enum-style access"""
        try:
            return DifficultyLevel(self.difficulty_level)
        except ValueError:
            return DifficultyLevel.MEDIUM  # Default fallback

    @difficulty.setter
    def difficulty(self, value):
        """Setter for backward compatibility"""
        if isinstance(value, DifficultyLevel):
            self.difficulty_level = value.value
        else:
            self.difficulty_level = str(value).lower()

    def is_answer_correct(self, answer):
        return answer.upper() == self.correct_answer

    def get_explanation(self):
        return self.explanation

    def to_dict(self, include_answer=False):
        data = {
            'id': self.id,
            'question_text': self.question_text,
            'options': self.get_options(),
            'difficulty_level': self.difficulty_level,
            'subject_id': self.subject_id,
            'topic_id': self.topic_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_answer:
            data.update({
                'correct_answer': self.correct_answer,
                'explanation': self.explanation
            })
        
        return data

    def __repr__(self):
        return f"<Question(id={self.id}, subject_id={self.subject_id}, topic_id={self.topic_id})>"