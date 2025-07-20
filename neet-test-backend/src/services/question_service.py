import time
import random
from random import sample, shuffle
from models.question import Question, DifficultyLevel
from models.subject import Subject
from models.topic import Topic
from database.connection import db
from sqlalchemy import and_
from services.gemini_service_new import GeminiService

class QuestionService:
    def __init__(self):
        self.ai_service = GeminiService()
        print("🔧 Using Google Gemini API for generating intelligent topic-specific questions.")

    def generate_questions(self, subject_id, topic_id=None, num_questions=5, difficulty=None):
        """Generate questions using Google Gemini for a specific subject"""
        try:
            # Verify subject exists
            subject = Subject.query.get(subject_id)
            if not subject:
                return {
                    'success': False,
                    'message': 'Subject not found'
                }, 404
            
            # Get topic name if topic_id provided
            topic_name = None
            if topic_id:
                topic = Topic.query.get(topic_id)
                if not topic:
                    return {
                        'success': False,
                        'message': 'Topic not found'
                    }, 404
                topic_name = topic.name
            
            # Validate difficulty
            if difficulty:
                if difficulty.lower() not in ['easy', 'medium', 'hard']:
                    return {
                        'success': False,
                        'message': 'Invalid difficulty level. Use: easy, medium, hard'
                    }, 400
            
            # Validate question count
            if num_questions < 1 or num_questions > 50:
                return {
                    'success': False,
                    'message': 'Question count must be between 1 and 50'
                }, 400
            
            # Generate questions using Google Gemini - DO NOT save to database for tests
            generated_questions = self.ai_service.generate_neet_questions(
                subject=subject.name,
                topic=topic_name,
                count=num_questions,
                difficulty=difficulty or 'medium'
            )
            
            if not generated_questions:
                return {
                    'success': False,
                    'message': 'Failed to generate questions. Please try again.'
                }, 500
            
            print(f"🔧 DEBUG: Generated questions from Gemini API: {len(generated_questions)}")
            
            # Validate each question has required fields
            valid_questions = []
            for i, q in enumerate(generated_questions):
                if all(key in q for key in ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']):
                    print(f"  Question {i}: Text='{q.get('question_text', 'MISSING')[:50]}...'")
                    valid_questions.append(q)
                else:
                    print(f"❌ Question {i} missing required fields")

            if not valid_questions:
                return {
                    'success': False,
                    'message': 'Failed to generate valid questions. Please try again.'
                }, 500

            generated_questions = valid_questions
            # Return questions directly without saving to database
            # We'll save them when the test is submitted along with user answers
            formatted_questions = []
            current_time = int(time.time())
            random_id = random.randint(1000, 9999)  # Add randomness
            
            for i, q_data in enumerate(generated_questions):
                # Always generate new IDs for fresh questions
                q_data['id'] = f"test_{current_time}_{random_id}_{i}"
                print(f"🔧 DEBUG: Assigned ID to question {i}: {q_data['id']}")
                    
                q_data['subject_id'] = subject_id
                q_data['topic_id'] = topic_id
                formatted_questions.append(q_data)
                
            print(f"✅ Final formatted questions: {[q['id'] for q in formatted_questions]}")
            print(f"🔧 DEBUG: Sample final question: {formatted_questions[0] if formatted_questions else 'None'}")
            
            return {
                'success': True,
                'questions': formatted_questions,
                'subject_name': subject.name,
                'topic_name': topic_name,
                'total_generated': len(formatted_questions),
                'difficulty': difficulty or 'medium',
                'timer_minutes': len(formatted_questions),  # 1 minute per question
                'message': f'Generated {len(formatted_questions)} fresh questions using AI'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating questions: {str(e)}'
            }, 500

    def get_question_by_id(self, question_id, include_answer=False):
        """Get a specific question by ID"""
        try:
            question = Question.query.get(question_id)
            if question:
                return question.to_dict(include_answer=include_answer)
            return None
        except Exception as e:
            print(f"Error getting question: {e}")
            return None

    def evaluate_answers(self, test_answers):
        """Evaluate user answers and return results"""
        results = []
        correct_count = 0
        
        for answer_data in test_answers:
            question_id = answer_data.get('question_id')
            user_answer = answer_data.get('answer', '').upper()
            
            question = Question.query.get(question_id)
            if question:
                is_correct = question.is_answer_correct(user_answer)
                if is_correct:
                    correct_count += 1
                
                results.append({
                    'question_id': question_id,
                    'user_answer': user_answer,
                    'correct_answer': question.correct_answer,
                    'is_correct': is_correct,
                    'explanation': question.explanation,
                    'question_text': question.question_text
                })
        
        total_questions = len(test_answers)
        score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        return {
            'results': results,
            'correct_count': correct_count,
            'total_questions': total_questions,
            'score_percentage': round(score_percentage, 2),
            'grade': self._get_grade(score_percentage)
        }

    def _get_grade(self, score_percentage):
        """Get grade based on score percentage"""
        if score_percentage >= 90:
            return "Excellent"
        elif score_percentage >= 75:
            return "Good"
        elif score_percentage >= 60:
            return "Average"
        elif score_percentage >= 40:
            return "Below Average"
        else:
            return "Poor"

    def _create_sample_questions(self, subject_id, topic_id=None):
        """Create sample questions for testing - now uses Azure OpenAI instead of hardcoded questions"""
        try:
            subject = Subject.query.get(subject_id)
            if not subject:
                return

            # Generate sample questions using Gemini API
            generated_questions = self.ai_service.generate_neet_questions(
                subject=subject.name,
                topic=None,  # Mixed topics for samples
                count=5,     # Generate 5 sample questions
                difficulty='medium'
            )
            
            if not generated_questions:
                print("❌ No questions generated from Gemini API")
                return
            
            for q_data in generated_questions:
                # Check if question already exists
                existing = Question.query.filter(
                    and_(
                        Question.question_text == q_data['question_text'],
                        Question.subject_id == subject_id
                    )
                ).first()
                
                if not existing:
                    question = Question(
                        question_text=q_data['question_text'],
                        option_a=q_data.get('option_a'),
                        option_b=q_data.get('option_b'),
                        option_c=q_data.get('option_c'),
                        option_d=q_data.get('option_d'),
                        correct_answer=q_data['correct_answer'],
                        explanation=q_data.get('explanation', ''),
                        subject_id=subject_id,
                        topic_id=topic_id or 1,
                        difficulty=DifficultyLevel(q_data.get('difficulty', 'medium')),
                        source='gemini_api'
                    )
                    db.session.add(question)
            
            db.session.commit()
            print(f"✅ Created {len(generated_questions)} sample questions for {subject.name}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating sample questions: {e}")

    def _get_sample_questions_data(self, subject_name, topic_id=None):
        """Deprecated: Now uses Gemini API for all question generation"""
        print(f"⚠️ _get_sample_questions_data called for {subject_name} - this method is deprecated")
        return []