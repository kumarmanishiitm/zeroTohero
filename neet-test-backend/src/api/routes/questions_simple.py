from flask import Blueprint, request, jsonify
from services.question_service import QuestionService

questions_bp = Blueprint('questions', __name__)
question_service = QuestionService()

@questions_bp.route('/questions/generate', methods=['GET'])
def generate_questions():
    """Generate questions for a selected subject"""
    try:
        # Get parameters from URL query string
        subject_id = request.args.get('subject_id', type=int)
        topic_id = request.args.get('topic_id', type=int)
        count = request.args.get('count', default=5, type=int)
        difficulty = request.args.get('difficulty', default='medium')

        if not subject_id:
            return jsonify({
                'success': False,
                'message': 'Subject ID is required. Use: ?subject_id=1'
            }), 400

        # Validate count
        if count < 1 or count > 50:
            return jsonify({
                'success': False,
                'message': 'Question count must be between 1 and 50'
            }), 400

        # Generate questions
        result, status_code = question_service.generate_questions(
            subject_id=subject_id,
            topic_id=topic_id,
            num_questions=count,
            difficulty=difficulty
        )
        
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate questions: {str(e)}'
        }), 500

@questions_bp.route('/questions/by-subject/<int:subject_id>', methods=['GET'])
def get_questions_by_subject(subject_id):
    """Get all questions for a specific subject"""
    try:
        from models.question import Question
        from models.subject import Subject
        
        # Verify subject exists
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({
                'success': False,
                'message': 'Subject not found'
            }), 404
        
        # Get questions for this subject
        questions = Question.query.filter_by(subject_id=subject_id).all()
        
        questions_data = [question.to_dict() for question in questions]
        
        return jsonify({
            'success': True,
            'subject_name': subject.name,
            'questions': questions_data,
            'total_count': len(questions_data)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch questions: {str(e)}'
        }), 500

@questions_bp.route('/questions/by-topic/<int:topic_id>', methods=['GET'])
def get_questions_by_topic(topic_id):
    """Get all questions for a specific topic"""
    try:
        from models.question import Question
        from models.topic import Topic
        
        # Verify topic exists
        topic = Topic.query.get(topic_id)
        if not topic:
            return jsonify({
                'success': False,
                'message': 'Topic not found'
            }), 404
        
        # Get questions for this topic
        questions = Question.query.filter_by(topic_id=topic_id).all()
        
        questions_data = [question.to_dict() for question in questions]
        
        return jsonify({
            'success': True,
            'topic_name': topic.name,
            'questions': questions_data,
            'total_count': len(questions_data)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch questions: {str(e)}'
        }), 500
