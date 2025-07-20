from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float, JSON
from database.connection import db
import enum

class TestStatus(enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class TestResult(db.Model):
    __tablename__ = 'test_results'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=True)  # Can be null for mixed tests
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False, default=0)
    wrong_answers = Column(Integer, nullable=False, default=0)
    not_attempted = Column(Integer, nullable=False, default=0)
    neet_score = Column(Integer, nullable=False, default=0)  # NEET score (+4/-1/0)
    max_score = Column(Integer, nullable=False, default=0)   # Maximum possible score
    score_percentage = Column(Float, nullable=False, default=0.0)
    time_taken = Column(Integer, nullable=True)  # in seconds
    status = Column(String(20), default=TestStatus.IN_PROGRESS.value)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __init__(self, user_id, subject_id, total_questions, topic_id=None, correct_answers=0, 
                 wrong_answers=0, not_attempted=0, neet_score=0, max_score=0, score_percentage=0.0, 
                 time_taken=0, status=None, started_at=None):
        self.user_id = user_id
        self.subject_id = subject_id
        self.topic_id = topic_id
        self.total_questions = total_questions
        self.correct_answers = correct_answers
        self.wrong_answers = wrong_answers
        self.not_attempted = not_attempted
        self.neet_score = neet_score
        self.max_score = max_score
        self.score_percentage = score_percentage
        self.time_taken = time_taken
        self.status = status or TestStatus.IN_PROGRESS.value
        self.started_at = started_at or datetime.utcnow()

    def calculate_score(self):
        if self.total_questions == 0:
            return 0.0
        self.score_percentage = (self.correct_answers / self.total_questions) * 100
        return self.score_percentage

    def complete_test(self):
        self.status = TestStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        self.calculate_score()

    def get_performance_grade(self):
        if self.score_percentage >= 90:
            return "Excellent"
        elif self.score_percentage >= 75:
            return "Good"
        elif self.score_percentage >= 60:
            return "Average"
        elif self.score_percentage >= 40:
            return "Below Average"
        else:
            return "Poor"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject_id': self.subject_id,
            'topic_id': self.topic_id,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'score_percentage': round(self.score_percentage, 2),
            'time_taken': self.time_taken,
            'status': self.status,
            'grade': self.get_performance_grade(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class TestAnswer(db.Model):
    __tablename__ = 'test_answers'

    id = Column(Integer, primary_key=True, index=True)
    test_result_id = Column(Integer, ForeignKey('test_results.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    user_answer = Column(String(1), nullable=True)  # A, B, C, D, or NULL for not attempted
    is_correct = Column(Boolean, nullable=False, default=False)
    time_taken = Column(Integer, nullable=True)  # in seconds
    answered_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, test_result_id, question_id, user_answer, is_correct, time_taken=None):
        self.test_result_id = test_result_id
        self.question_id = question_id
        self.user_answer = user_answer.upper() if user_answer else None  # Handle empty answers
        self.is_correct = is_correct
        self.time_taken = time_taken

    def to_dict(self):
        return {
            'id': self.id,
            'test_result_id': self.test_result_id,
            'question_id': self.question_id,
            'user_answer': self.user_answer,
            'is_correct': self.is_correct,
            'time_taken': self.time_taken,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None
        }