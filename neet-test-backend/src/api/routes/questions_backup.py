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

        if num_questions < 1 or num_questions > 50:
            return jsonify({
                'success': False,
                'message': 'Number of questions must be between 1 and 50'
            }), 400

        questions = question_service.generate_questions(
            subject_id=subject_id,
            topic_id=topic_id,
            num_questions=num_questions,
            difficulty=difficulty
        )

        if not questions:
            return jsonify({
                'success': False,
                'message': 'No questions available for the selected criteria'
            }), 404

        return jsonify({
            'success': True,
            'questions': questions,
            'total_count': len(questions),
            'metadata': {
                'subject_id': subject_id,
                'topic_id': topic_id,
                'difficulty': difficulty
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate questions: {str(e)}'
        }), 500

@questions_bp.route('/questions/<int:question_id>', methods=['GET'])
@token_required
def get_question(current_user, question_id):
    """Get a specific question by ID"""
    try:
        include_answer = request.args.get('include_answer', 'false').lower() == 'true'
        
        question = question_service.get_question_by_id(
            question_id=question_id,
            include_answer=include_answer
        )

        if not question:
            return jsonify({
                'success': False,
                'message': 'Question not found'
            }), 404

        return jsonify({
            'success': True,
            'question': question
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch question: {str(e)}'
        }), 500

@questions_bp.route('/questions/evaluate', methods=['POST'])
@token_required
def evaluate_answers(current_user):
    """Evaluate answers for practice questions (not part of a formal test)"""
    try:
        data = request.get_json()
        
        if not data or 'answers' not in data:
            return jsonify({
                'success': False,
                'message': 'Answers are required'
            }), 400

        answers = data['answers']
        
        if not isinstance(answers, list) or len(answers) == 0:
            return jsonify({
                'success': False,
                'message': 'Answers must be a non-empty list'
            }), 400

        # Validate answer format
        for answer in answers:
            if not isinstance(answer, dict) or 'question_id' not in answer or 'answer' not in answer:
                return jsonify({
                    'success': False,
                    'message': 'Each answer must contain question_id and answer'
                }), 400

        results = question_service.evaluate_answers(answers)

        return jsonify({
            'success': True,
            'evaluation': results
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to evaluate answers: {str(e)}'
        }), 500

@questions_bp.route('/questions/by-subject/<int:subject_id>', methods=['GET'])
@token_required
def get_questions_by_subject(current_user, subject_id):
    """Get all questions for a subject with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        topic_id = request.args.get('topic_id', type=int)
        difficulty = request.args.get('difficulty')

        if per_page > 50:
            per_page = 50

        from src.models.question import Question
        
        query = Question.query.filter_by(subject_id=subject_id)
        
        if topic_id:
            query = query.filter_by(topic_id=topic_id)
            
        if difficulty:
            from src.models.question import DifficultyLevel
            try:
                difficulty_enum = DifficultyLevel(difficulty)
                query = query.filter_by(difficulty=difficulty_enum)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid difficulty level'
                }), 400

        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        questions = [q.to_dict(include_answer=False) for q in paginated.items]

        return jsonify({
            'success': True,
            'questions': questions,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch questions: {str(e)}'
        }), 500

@questions_bp.route('/questions/by-topic/<int:topic_id>', methods=['GET'])
@token_required
def get_questions_by_topic(current_user, topic_id):
    """Get all questions for a topic"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        difficulty = request.args.get('difficulty')

        if per_page > 50:
            per_page = 50

        from src.models.question import Question
        
        query = Question.query.filter_by(topic_id=topic_id)
            
        if difficulty:
            from src.models.question import DifficultyLevel
            try:
                difficulty_enum = DifficultyLevel(difficulty)
                query = query.filter_by(difficulty=difficulty_enum)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid difficulty level'
                }), 400

        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        questions = [q.to_dict(include_answer=False) for q in paginated.items]

        return jsonify({
            'success': True,
            'questions': questions,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch questions: {str(e)}'
        }), 500

@questions_bp.route('/questions/search', methods=['GET'])
@token_required
def search_questions(current_user):
    """Search questions by text"""
    try:
        query_text = request.args.get('q', '').strip()
        subject_id = request.args.get('subject_id', type=int)
        topic_id = request.args.get('topic_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if not query_text:
            return jsonify({
                'success': False,
                'message': 'Search query is required'
            }), 400

        if per_page > 50:
            per_page = 50

        from src.models.question import Question
        
        query = Question.query.filter(
            Question.question_text.contains(query_text)
        )
        
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
            
        if topic_id:
            query = query.filter_by(topic_id=topic_id)

        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        questions = [q.to_dict(include_answer=False) for q in paginated.items]

        return jsonify({
            'success': True,
            'questions': questions,
            'search_query': query_text,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to search questions: {str(e)}'
        }), 500