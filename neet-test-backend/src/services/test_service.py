from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import joinedload
import random

from database.connection import db
from models.test import TestResult, TestAnswer
from models.question import Question
from models.subject import Subject
from models.topic import Topic
from services.question_service import QuestionService
from enum import Enum

class TestStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"

class TestService:
    def __init__(self):
        self.question_service = QuestionService()
    
    def start_test(self, user_id: int, subject_id: int, topic_id: int = None, question_count: int = 10) -> Dict[str, Any]:
        """Start a new test session with timer functionality"""
        try:
            # Validate subject
            subject = Subject.query.get(subject_id)
            if not subject:
                return {
                    'success': False,
                    'message': 'Subject not found'
                }, 404
            
            # Validate topic if provided
            topic = None
            if topic_id:
                topic = Topic.query.get(topic_id)
                if not topic or topic.subject_id != subject_id:
                    return {
                        'success': False,
                        'message': 'Topic not found or does not belong to the specified subject'
                    }, 404
            
            # Generate fresh questions using Azure OpenAI service - NO database questions
            print(f"🎯 Generating {question_count} fresh questions from Azure OpenAI...")
            
            # Get topic name for question generation
            topic_name = topic.name if topic else None
            
            # Use QuestionService to generate fresh questions (this uses Azure OpenAI)
            question_result, status_code = self.question_service.generate_questions(
                subject_id=subject_id,
                topic_id=topic_id,
                num_questions=question_count,
                difficulty='medium'  # Default difficulty for tests
            )
            
            if not question_result.get('success'):
                return {
                    'success': False,
                    'message': f'Failed to generate questions: {question_result.get("message", "Unknown error")}'
                }, status_code
            
            # Get the generated questions from the service response
            generated_questions = question_result.get('questions', [])
            
            if len(generated_questions) < question_count:
                return {
                    'success': False,
                    'message': f'Could not generate enough questions. Requested: {question_count}, Generated: {len(generated_questions)}'
                }, 500
            
            # Create test result record FIRST so we have subject_id and topic_id
            test_result = TestResult(
                user_id=user_id,
                subject_id=subject_id,
                topic_id=topic_id,
                total_questions=question_count,
                correct_answers=0,
                score_percentage=0.0,
                time_taken=0,
                status=TestStatus.IN_PROGRESS.value,
                started_at=datetime.utcnow()
            )
            
            db.session.add(test_result)
            db.session.commit()
            
            # Save the original Azure OpenAI questions to database BEFORE transformation
            print(f"🔧 DEBUG: Saving {len(generated_questions)} original questions to database...")
            for i, gq in enumerate(generated_questions):
                print(f"  Original Question {i}: ID={gq.get('id')}, Keys={list(gq.keys())}")
            question_id_mapping = self._save_test_questions_to_database(generated_questions, test_result.subject_id, test_result.topic_id)
            print(f"🔧 DEBUG: Original questions saved. ID mapping: {question_id_mapping}")
            
            # Now format questions for frontend response - handle both database and direct Azure OpenAI formats
            questions = []
            for question in generated_questions:
                # Handle both formats: database questions (with options dict) and direct Azure OpenAI responses
                if 'options' in question:
                    # Database question format
                    options = question['options']
                else:
                    # Direct Azure OpenAI format - convert to options object
                    options = {
                        'A': question.get('option_a'),
                        'B': question.get('option_b'),
                        'C': question.get('option_c'),
                        'D': question.get('option_d')
                    }
                
                questions.append({
                    'id': question.get('id'),  # For frontend compatibility
                    'question_id': question.get('id'),  # For API consistency
                    'question_text': question.get('question_text'),
                    'options': options,
                    'subject_id': question.get('subject_id'),
                    'topic_id': question.get('topic_id')
                })
            
            print(f"✅ Generated {len(questions)} fresh questions from Azure OpenAI!")
            
            # Calculate timer (1 minute per question)
            timer_minutes = question_count
            timer_seconds = timer_minutes * 60
            end_time = datetime.utcnow() + timedelta(minutes=timer_minutes)
            
            return {
                'success': True,
                'test_id': test_result.id,
                'questions': questions,
                'total_questions': len(questions),
                'timer_minutes': timer_minutes,
                'timer_seconds': timer_seconds,
                'start_time': test_result.started_at.isoformat(),
                'end_time': end_time.isoformat(),
                'auto_submit_at': end_time.isoformat(),
                'message': f'Test started! You have {timer_minutes} minutes to complete {question_count} questions.',
                'instructions': [
                    f'Total time: {timer_minutes} minutes ({timer_seconds} seconds)',
                    'Test will auto-submit when timer expires',
                    'Each question is worth equal points',
                    'Choose the best answer for each question'
                ]
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Failed to start test: {str(e)}'
            }, 500
    
    def submit_test(self, test_id: int, answers: List[Dict[str, Any]], test_questions: List[Dict[str, Any]] = None, force_submit: bool = False) -> Dict[str, Any]:
        """Submit test answers and calculate results"""
        try:
            # Get test result
            test_result = TestResult.query.get(test_id)
            if not test_result:
                return {
                    'success': False,
                    'message': 'Test not found'
                }, 404
            
            if test_result.status == TestStatus.COMPLETED.value:
                return {
                    'success': False,
                    'message': 'Test already completed'
                }, 400
            
            # Calculate time taken
            time_taken = int((datetime.utcnow() - test_result.started_at).total_seconds())
            
            # Check if test expired - but don't block submission, just flag it
            expected_duration = test_result.total_questions * 60  # 1 minute per question
            is_expired = time_taken > expected_duration
            
            # Create question ID mapping for questions that should already be in database
            question_id_mapping = {}
            if test_questions:
                print(f"🔧 DEBUG: Creating mapping for {len(test_questions)} test questions...")
                for i, tq in enumerate(test_questions):
                    print(f"  Question {i}: ID={tq.get('id')}, Text='{tq.get('question_text', '')[:50]}...'")
                    
                    # Find existing question in database by question text and subject
                    existing_question = Question.query.filter_by(
                        question_text=tq.get('question_text'),
                        subject_id=test_result.subject_id
                    ).first()
                    
                    if existing_question:
                        question_id_mapping[str(tq.get('id'))] = existing_question.id
                        print(f"🔧 DEBUG: Mapped {tq.get('id')} -> {existing_question.id}")
                    else:
                        print(f"⚠️ Warning: Question not found in database: {tq.get('question_text', '')[:50]}...")
                
                print(f"🔧 DEBUG: Question ID mapping created: {question_id_mapping}")
            else:
                print("🔧 DEBUG: No test_questions provided to submit_test")
            
            # Process answers and get all questions for this test
            correct_count = 0
            answer_details = []
            answered_question_ids = set()
            
            # First, process submitted answers
            for answer_data in answers:
                question_identifier = answer_data.get('question_id')
                user_answer = answer_data.get('answer', '').strip().upper()
                answered_question_ids.add(question_identifier)
                
                print(f"🔧 DEBUG: Processing answer - question_id: '{question_identifier}', user_answer: '{user_answer}'")
                
                # Handle both database questions and fresh Azure OpenAI questions
                question = None
                correct_answer = None
                question_text = ""
                explanation = ""
                options = {}
                actual_question_id = None
                
                # Try to get from database first
                if isinstance(question_identifier, int) or (isinstance(question_identifier, str) and question_identifier.isdigit()):
                    question = Question.query.get(int(question_identifier))
                    if question:
                        actual_question_id = question.id
                
                # Store fresh question data for later use
                fresh_question_data = None
                if not question:
                    # Fresh question from Azure OpenAI - find it in test_questions and mapping
                    for tq in test_questions or []:
                        if str(tq.get('id')) == str(question_identifier):
                            fresh_question_data = tq
                            break
                    
                    if fresh_question_data:
                        correct_answer = fresh_question_data.get('correct_answer')
                        question_text = fresh_question_data.get('question_text', '')
                        explanation = fresh_question_data.get('explanation', '')
                        
                        # Handle both question formats: original Azure OpenAI (option_a/option_b/etc.) 
                        # and transformed format (options object)
                        if 'options' in fresh_question_data and fresh_question_data['options']:
                            # Transformed format with options object
                            options_obj = fresh_question_data['options']
                            options = {
                                'A': options_obj.get('A'),
                                'B': options_obj.get('B'),
                                'C': options_obj.get('C'),
                                'D': options_obj.get('D')
                            }
                        else:
                            # Original Azure OpenAI format with individual option fields
                            options = {
                                'A': fresh_question_data.get('option_a'),
                                'B': fresh_question_data.get('option_b'),
                                'C': fresh_question_data.get('option_c'),
                                'D': fresh_question_data.get('option_d')
                            }
                        
                        # Get the mapped database question ID
                        actual_question_id = question_id_mapping.get(str(question_identifier))
                        if actual_question_id:
                            question = Question.query.get(actual_question_id)
                
                if question:
                    # Use database question data
                    correct_answer = question.correct_answer
                    question_text = question.question_text
                    explanation = question.explanation
                    options = question.get_options()
                    actual_question_id = question.id
                
                # Only count as attempted if user provided an answer
                is_attempted = bool(user_answer)
                is_correct = False
                
                if is_attempted and correct_answer:
                    is_correct = user_answer == correct_answer.upper()
                    if is_correct:
                        correct_count += 1
                
                # Save test answer - ALWAYS save, even if mapping fails
                save_question_id = actual_question_id
                print(f"🔧 DEBUG: actual_question_id = {actual_question_id}")
                print(f"🔧 DEBUG: fresh_question_data available = {fresh_question_data is not None}")
                
                if not save_question_id and fresh_question_data:
                    # If mapping failed but we have fresh question data, create/find the question
                    print(f"🔧 DEBUG: Mapping failed for '{question_identifier}', creating question in database...")
                    save_question_id = self._ensure_question_exists(fresh_question_data, test_result.subject_id, test_result.topic_id)
                    print(f"🔧 DEBUG: Created/found question with ID: {save_question_id}")
                
                if save_question_id:
                    print(f"🔧 DEBUG: Saving TestAnswer with question_id: {save_question_id}")
                    test_answer = TestAnswer(
                        test_result_id=test_id,
                        question_id=save_question_id,
                        user_answer=user_answer if is_attempted else None,
                        is_correct=is_correct,
                        time_taken=answer_data.get('time_taken', 0)
                    )
                    db.session.add(test_answer)
                else:
                    print(f"🔧 DEBUG: FAILED to get question_id for '{question_identifier}' - TestAnswer NOT saved!")
                    print(f"🔧 DEBUG: Debug info - actual_question_id: {actual_question_id}, fresh_question_data: {fresh_question_data is not None}")
                    if fresh_question_data:
                        print(f"🔧 DEBUG: Fresh question data keys: {list(fresh_question_data.keys())}")
                        print(f"🔧 DEBUG: Fresh question text: {fresh_question_data.get('question_text', 'N/A')[:50]}...")
                
                # Add to answer details
                answer_details.append({
                    'question_id': actual_question_id or question_identifier,
                    'question_text': question_text,
                    'user_answer': user_answer if is_attempted else 'Not Attempted',
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'is_attempted': is_attempted,
                    'explanation': explanation,
                    'options': options
                })
            
            # Calculate score using NEET marking scheme
            total_submitted_questions = len(answers)
            attempted_questions = len([a for a in answers if a.get('answer', '').strip()])
            wrong_answers = attempted_questions - correct_count
            not_attempted = total_submitted_questions - attempted_questions
            
            # NEET scoring: +4 for correct, -1 for wrong, 0 for not attempted
            neet_score = (correct_count * 4) - (wrong_answers * 1)
            max_possible_score = total_submitted_questions * 4
            
            # Calculate percentage based on NEET score
            score_percentage = max(0, (neet_score / max_possible_score * 100)) if max_possible_score > 0 else 0
            
            # Update test result with actual submitted question count
            test_result.total_questions = total_submitted_questions
            test_result.correct_answers = correct_count
            test_result.wrong_answers = wrong_answers
            test_result.not_attempted = not_attempted
            test_result.neet_score = neet_score
            test_result.max_score = max_possible_score
            test_result.score_percentage = score_percentage
            test_result.time_taken = time_taken
            test_result.status = TestStatus.COMPLETED.value
            test_result.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            # Generate performance analysis
            performance = self._analyze_performance(score_percentage, time_taken, expected_duration)
            
            return {
                'success': True,
                'test_id': test_id,
                'results': {
                    'correct_answers': correct_count,
                    'wrong_answers': wrong_answers,
                    'not_attempted': not_attempted,
                    'total_questions': total_submitted_questions,
                    'neet_score': neet_score,
                    'max_score': max_possible_score,
                    'score_percentage': round(score_percentage, 2),
                    'grade': performance['grade'],
                    'time_taken_minutes': round(time_taken / 60, 1),
                    'time_taken_seconds': time_taken,
                    'expected_time_minutes': round(expected_duration / 60, 1)
                },
                'performance_analysis': performance,
                'answer_details': answer_details,
                'message': f'Test completed! You scored {correct_count}/{total_submitted_questions} ({round(score_percentage, 1)}%)'
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Failed to submit test: {str(e)}'
            }, 500
    
    def get_test_status(self, test_id: int) -> Dict[str, Any]:
        """Get current test status and time remaining"""
        try:
            test_result = TestResult.query.get(test_id)
            if not test_result:
                return {
                    'success': False,
                    'message': 'Test not found'
                }, 404
            
            # Calculate time details
            now = datetime.utcnow()
            time_elapsed = int((now - test_result.started_at).total_seconds())
            expected_duration = test_result.total_questions * 60  # 1 minute per question
            time_remaining = max(0, expected_duration - time_elapsed)
            
            # Check if test should be auto-expired
            is_expired = time_remaining <= 0 and test_result.status == TestStatus.IN_PROGRESS.value
            
            if is_expired:
                test_result.status = TestStatus.EXPIRED.value
                db.session.commit()
            
            return {
                'success': True,
                'test_id': test_id,
                'status': test_result.status,
                'time_elapsed_seconds': time_elapsed,
                'time_remaining_seconds': time_remaining,
                'time_remaining_minutes': round(time_remaining / 60, 1),
                'is_expired': is_expired,
                'total_questions': test_result.total_questions,
                'expected_duration_minutes': round(expected_duration / 60, 1)
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get test status: {str(e)}'
            }, 500
    
    def get_test_results(self, test_id: int) -> Dict[str, Any]:
        """Get detailed test results"""
        try:
            test_result = TestResult.query.get(test_id)
            
            if not test_result:
                return {
                    'success': False,
                    'message': 'Test not found'
                }, 404
            
            # Get subject and topic information separately
            subject = Subject.query.get(test_result.subject_id)
            topic = Topic.query.get(test_result.topic_id) if test_result.topic_id else None
            
            # Get all test answers
            test_answers = TestAnswer.query.filter_by(test_result_id=test_id).all()
            
            answer_details = []
            for answer in test_answers:
                question = Question.query.get(answer.question_id)
                if question:
                    answer_details.append({
                        'question_id': question.id,
                        'question_text': question.question_text,
                        'user_answer': answer.user_answer,
                        'correct_answer': question.correct_answer,
                        'is_correct': answer.is_correct,
                        'explanation': question.explanation,
                        'options': question.get_options(),
                        'time_taken': answer.time_taken
                    })
            
            # Performance analysis
            performance = self._analyze_performance(
                test_result.score_percentage,
                test_result.time_taken or 0,
                test_result.total_questions * 60
            )
            
            # Safely get new columns with fallbacks
            wrong_answers = getattr(test_result, 'wrong_answers', None)
            if wrong_answers is None:
                wrong_answers = test_result.total_questions - test_result.correct_answers
            
            not_attempted = getattr(test_result, 'not_attempted', None)
            if not_attempted is None:
                not_attempted = 0
                
            neet_score = getattr(test_result, 'neet_score', None)
            if neet_score is None:
                neet_score = (test_result.correct_answers * 4) - (wrong_answers * 1)
                
            max_score = getattr(test_result, 'max_score', None)
            if max_score is None:
                max_score = test_result.total_questions * 4
            
            return {
                'success': True,
                'test_id': test_id,
                'subject': subject.name if subject else 'Unknown',
                'topic': topic.name if topic else None,
                'status': test_result.status,
                'started_at': test_result.started_at.isoformat() if test_result.started_at else None,
                'completed_at': test_result.completed_at.isoformat() if test_result.completed_at else None,
                'results': {
                    'correct_answers': test_result.correct_answers,
                    'wrong_answers': wrong_answers,
                    'not_attempted': not_attempted,
                    'total_questions': test_result.total_questions,
                    'neet_score': neet_score,
                    'max_score': max_score,
                    'score_percentage': test_result.score_percentage,
                    'grade': performance['grade'],
                    'time_taken_minutes': round((test_result.time_taken or 0) / 60, 1),
                    'time_taken_seconds': test_result.time_taken or 0
                },
                'performance_analysis': performance,
                'answer_details': answer_details
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get test results: {str(e)}'
            }, 500
    
    def _analyze_performance(self, score_percentage: float, time_taken: int, expected_time: int) -> Dict[str, Any]:
        """Analyze test performance"""
        
        # Grade calculation
        if score_percentage >= 90:
            grade = "Excellent"
            grade_message = "Outstanding performance! You have excellent command over the subject."
        elif score_percentage >= 75:
            grade = "Good" 
            grade_message = "Good job! You have a solid understanding of the concepts."
        elif score_percentage >= 60:
            grade = "Average"
            grade_message = "Average performance. Consider reviewing the topics you missed."
        elif score_percentage >= 40:
            grade = "Below Average"
            grade_message = "Below average score. Focus on strengthening your fundamentals."
        else:
            grade = "Poor"
            grade_message = "Poor performance. Significant improvement needed. Consider additional study."
        
        return {
            'grade': grade,
            'grade_message': grade_message
        }

    def get_user_test_history(self, user_id: int) -> Dict[str, Any]:
        """Get user's test history with detailed information"""
        try:
            # Get all completed tests for the user
            test_results = TestResult.query.filter_by(
                user_id=user_id, 
                status=TestStatus.COMPLETED.value
            ).order_by(TestResult.completed_at.desc()).all()
            
            tests = []
            for test in test_results:
                # Get subject and topic information
                subject = Subject.query.get(test.subject_id)
                topic = Topic.query.get(test.topic_id) if test.topic_id else None
                
                # Safely get new columns with fallbacks for old data
                wrong_answers = getattr(test, 'wrong_answers', None)
                if wrong_answers is None:
                    wrong_answers = max(0, test.total_questions - test.correct_answers)
                
                not_attempted = getattr(test, 'not_attempted', None)
                if not_attempted is None:
                    not_attempted = 0
                
                neet_score = getattr(test, 'neet_score', None)
                if neet_score is None:
                    neet_score = (test.correct_answers * 4) - (wrong_answers * 1)
                
                max_score = getattr(test, 'max_score', None)
                if max_score is None:
                    max_score = test.total_questions * 4
                
                test_data = {
                    'id': test.id,
                    'test_id': test.id,
                    'test_name': f"{subject.name if subject else 'Unknown'} Test",
                    'subject': subject.name if subject else 'Unknown',
                    'topic': topic.name if topic else None,
                    'total_questions': test.total_questions,
                    'correct_answers': test.correct_answers,
                    'wrong_answers': wrong_answers,
                    'not_attempted': not_attempted,
                    'score_percentage': test.score_percentage,
                    'neet_score': neet_score,
                    'max_score': max_score,
                    'time_taken_minutes': round(test.time_taken / 60, 1) if test.time_taken else 0,
                    'started_at': test.started_at.isoformat() if test.started_at else None,
                    'completed_at': test.completed_at.isoformat() if test.completed_at else None,
                    'date': test.completed_at.isoformat() if test.completed_at else test.started_at.isoformat()
                }
                tests.append(test_data)
            
            return {
                'success': True,
                'tests': tests,
                'total_tests': len(tests)
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get test history: {str(e)}'
            }, 500

    def get_user_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user analytics"""
        try:
            # Get all completed tests
            test_results = TestResult.query.filter_by(
                user_id=user_id, 
                status=TestStatus.COMPLETED.value
            ).order_by(TestResult.completed_at.desc()).all()
            
            if not test_results:
                return {
                    'success': True,
                    'analytics': {
                        'total_tests': 0,
                        'average_score': 0,
                        'best_score': 0,
                        'recent_scores': [],
                        'subject_performance': {}
                    }
                }, 200
            
            # Calculate basic statistics
            total_tests = len(test_results)
            scores = [test.score_percentage for test in test_results]
            average_score = sum(scores) / len(scores)
            best_score = max(scores)
            
            # Recent scores for trend analysis (last 10 tests)
            recent_scores = scores[:10]
            
            # Subject-wise performance
            subject_performance = {}
            for test in test_results:
                subject = Subject.query.get(test.subject_id)
                subject_name = subject.name.lower() if subject else 'unknown'
                
                if subject_name not in subject_performance:
                    subject_performance[subject_name] = {
                        'scores': [],
                        'tests': []
                    }
                
                subject_performance[subject_name]['scores'].append(test.score_percentage)
                subject_performance[subject_name]['tests'].append({
                    'id': test.id,
                    'score': test.score_percentage,
                    'date': test.completed_at.isoformat() if test.completed_at else None
                })
            
            # Calculate subject statistics
            for subject, data in subject_performance.items():
                scores = data['scores']
                subject_performance[subject] = {
                    'average': sum(scores) / len(scores),
                    'best': max(scores),
                    'count': len(scores),
                    'recent_tests': data['tests'][:5]  # Last 5 tests
                }
            
            analytics = {
                'total_tests': total_tests,
                'average_score': round(average_score, 2),
                'best_score': round(best_score, 2),
                'recent_scores': recent_scores,
                'subject_performance': subject_performance,
                'performance_trend': self._calculate_trend(recent_scores),
                'test_frequency': self._calculate_test_frequency(test_results),
                'improvement_suggestions': self._get_improvement_suggestions(subject_performance, average_score)
            }
            
            return {
                'success': True,
                'analytics': analytics
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get analytics: {str(e)}'
            }, 500

    def _calculate_trend(self, recent_scores: List[float]) -> Dict[str, Any]:
        """Calculate performance trend from recent scores"""
        if len(recent_scores) < 2:
            return {'direction': 'stable', 'change': 0}
        
        latest = recent_scores[0]
        previous = recent_scores[1]
        change = latest - previous
        
        if change > 5:
            direction = 'improving'
        elif change < -5:
            direction = 'declining'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'change': round(change, 1),
            'latest_score': latest,
            'previous_score': previous
        }

    def _calculate_test_frequency(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """Calculate how frequently user takes tests"""
        if len(test_results) < 2:
            return {'tests_per_week': 0, 'last_test_days_ago': 0}
        
        # Calculate average days between tests
        dates = [test.completed_at for test in test_results if test.completed_at]
        if len(dates) < 2:
            return {'tests_per_week': 0, 'last_test_days_ago': 0}
        
        dates.sort(reverse=True)
        total_days = (dates[0] - dates[-1]).days
        tests_per_week = len(dates) / (total_days / 7) if total_days > 0 else 0
        
        last_test_days_ago = (datetime.utcnow() - dates[0]).days
        
        return {
            'tests_per_week': round(tests_per_week, 1),
            'last_test_days_ago': last_test_days_ago
        }

    def _get_improvement_suggestions(self, subject_performance: Dict, overall_average: float) -> List[str]:
        """Generate personalized improvement suggestions"""
        suggestions = []
        
        # Find weakest subject
        if subject_performance:
            weakest_subject = min(subject_performance.items(), key=lambda x: x[1]['average'])
            if weakest_subject[1]['average'] < 60:
                suggestions.append(f"Focus more on {weakest_subject[0].title()} - your average score is {weakest_subject[1]['average']:.1f}%")
        
        # Overall performance suggestions
        if overall_average < 50:
            suggestions.append("Consider reviewing fundamental concepts and taking more practice tests")
        elif overall_average < 70:
            suggestions.append("Good progress! Focus on time management and accuracy")
        else:
            suggestions.append("Excellent performance! Keep practicing to maintain consistency")
        
        return suggestions

    def _save_test_questions_to_database(self, test_questions: List[Dict[str, Any]], subject_id: int, topic_id: int = None) -> Dict[str, int]:
        """Save fresh Azure OpenAI questions to database for test history and return mapping"""
        question_id_mapping = {}
        try:
            for i, question_data in enumerate(test_questions):
                print(f"🔧 DEBUG: Processing question {i} for saving - keys: {list(question_data.keys())}")
                print(f"🔧 DEBUG: Question {i} data: {question_data}")
                
                # Check if question already exists (avoid duplicates)
                existing_question = Question.query.filter_by(
                    question_text=question_data.get('question_text'),
                    subject_id=subject_id
                ).first()
                
                if existing_question:
                    # Use existing question
                    question_id_mapping[str(question_data.get('id'))] = existing_question.id
                    print(f"🔧 DEBUG: Using existing question with ID: {existing_question.id}")
                else:
                    # Handle both question formats: original Azure OpenAI (option_a/option_b/etc.) 
                    # and transformed format (options object)
                    if 'options' in question_data and question_data['options']:
                        # Transformed format with options object
                        print(f"🔧 DEBUG: Question {i} has transformed format with options object")
                        options = question_data['options']
                        option_a = options.get('A')
                        option_b = options.get('B')
                        option_c = options.get('C')
                        option_d = options.get('D')
                        print(f"🔧 DEBUG: Extracted options - A: {option_a}, B: {option_b}, C: {option_c}, D: {option_d}")
                    else:
                        # Original Azure OpenAI format with individual option fields
                        print(f"🔧 DEBUG: Question {i} has original format with individual option fields")
                        option_a = question_data.get('option_a')
                        option_b = question_data.get('option_b')
                        option_c = question_data.get('option_c')
                        option_d = question_data.get('option_d')
                        print(f"🔧 DEBUG: Direct options - A: {option_a}, B: {option_b}, C: {option_c}, D: {option_d}")
                    
                    # Validate that we have the required options
                    if not all([option_a, option_b, option_c, option_d]):
                        print(f"⚠️ Skipping question {i} - missing option data")
                        continue
                    
                    # Create new question in database
                    new_question = Question(
                        question_text=question_data.get('question_text'),
                        option_a=option_a,
                        option_b=option_b,
                        option_c=option_c,
                        option_d=option_d,
                        correct_answer=question_data.get('correct_answer'),
                        explanation=question_data.get('explanation', ''),
                        subject_id=subject_id,
                        topic_id=topic_id,
                        difficulty=question_data.get('difficulty', 'medium'),
                        source='azure_openai'  # Mark as AI-generated
                    )
                    
                    db.session.add(new_question)
                    db.session.flush()  # Get the ID before commit
                    question_id_mapping[str(question_data.get('id'))] = new_question.id
                    print(f"🔧 DEBUG: Created new question with ID: {new_question.id}")
                    
            db.session.commit()
            print(f"✅ Saved {len(question_id_mapping)} fresh questions to database")
            
        except Exception as e:
            print(f"⚠️ Error saving questions to database: {e}")
            db.session.rollback()
        
        return question_id_mapping
    
    def _create_question_mapping(self, test_questions: List[Dict[str, Any]], answers: List[Dict[str, Any]]) -> Dict[str, int]:
        """Create mapping from test question IDs to database question IDs"""
        mapping = {}
        
        for answer in answers:
            question_id = answer.get('question_id')
            # Find matching test question
            for tq in test_questions:
                if str(tq.get('id')) == str(question_id):
                    # Try to find in database
                    saved_question = self._find_saved_question(tq)
                    if saved_question:
                        mapping[str(question_id)] = saved_question.id
                    break
        
        return mapping
    
    def _find_saved_question(self, question_data: Dict[str, Any]) -> Question:
        """Find a saved question in database based on question data"""
        try:
            # Try to find by question text (most reliable)
            question = Question.query.filter_by(
                question_text=question_data.get('question_text')
            ).first()
            
            return question
            
        except Exception as e:
            print(f"Error finding saved question: {e}")
            return None
    
    def _ensure_question_exists(self, question_data: Dict[str, Any], subject_id: int, topic_id: int = None) -> int:
        """Ensure a question exists in database and return its ID"""
        try:
            print(f"🔧 DEBUG: _ensure_question_exists called with question_data keys: {list(question_data.keys())}")
            print(f"🔧 DEBUG: Question data: {question_data}")
            
            # Try to find existing question first
            existing_question = Question.query.filter_by(
                question_text=question_data.get('question_text'),
                subject_id=subject_id
            ).first()
            
            if existing_question:
                print(f"🔧 DEBUG: Found existing question with ID: {existing_question.id}")
                return existing_question.id
            
            # Handle both question formats: original Azure OpenAI (option_a/option_b/etc.) 
            # and transformed format (options object)
            if 'options' in question_data and question_data['options']:
                # Transformed format with options object
                print(f"🔧 DEBUG: Using transformed format with options object")
                options = question_data['options']
                option_a = options.get('A')
                option_b = options.get('B')
                option_c = options.get('C')
                option_d = options.get('D')
                print(f"🔧 DEBUG: Extracted options - A: {option_a}, B: {option_b}, C: {option_c}, D: {option_d}")
            else:
                # Original Azure OpenAI format with individual option fields
                print(f"🔧 DEBUG: Using original format with individual option fields")
                option_a = question_data.get('option_a')
                option_b = question_data.get('option_b')
                option_c = question_data.get('option_c')
                option_d = question_data.get('option_d')
                print(f"🔧 DEBUG: Direct options - A: {option_a}, B: {option_b}, C: {option_c}, D: {option_d}")
            
            # Validate that we have the required options
            if not all([option_a, option_b, option_c, option_d]):
                print(f"⚠️ Missing option data - A: {option_a}, B: {option_b}, C: {option_c}, D: {option_d}")
                print(f"⚠️ Original question data: {question_data}")
                return None
            
            # Create new question if not found
            new_question = Question(
                question_text=question_data.get('question_text'),
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=question_data.get('correct_answer'),
                explanation=question_data.get('explanation', ''),
                subject_id=subject_id,
                topic_id=topic_id,
                difficulty=question_data.get('difficulty', 'medium'),
                source='azure_openai'
            )
            
            db.session.add(new_question)
            db.session.flush()  # Get the ID immediately
            print(f"🔧 DEBUG: Created new question with ID: {new_question.id}")
            return new_question.id
            
        except Exception as e:
            print(f"⚠️ Error ensuring question exists: {e}")
            print(f"⚠️ Question data that failed: {question_data}")
            return None
