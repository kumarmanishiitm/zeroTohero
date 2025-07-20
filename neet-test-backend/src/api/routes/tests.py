from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.test_service import TestService

tests_bp = Blueprint('tests', __name__)
test_service = TestService()

@tests_bp.route('/tests/start', methods=['POST'])
@jwt_required()
def start_test():
    """Start a new test with timer functionality"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        print(f"DEBUG: start_test called with user_id={user_id}, data={data}")
        
        if not data:
            print("DEBUG: No request data provided")
            return jsonify({
                'success': False,
                'message': 'Request data is required'
            }), 400

        subject_id = data.get('subject_id')
        topic_id = data.get('topic_id')  # Optional - can be None for mixed tests
        question_count = data.get('question_count', 10)

        if not subject_id:
            return jsonify({
                'success': False,
                'message': 'Subject ID is required'
            }), 400

        if question_count < 1 or question_count > 100:
            return jsonify({
                'success': False,
                'message': 'Number of questions must be between 1 and 100'
            }), 400
        
        result, status_code = test_service.start_test(
            user_id=user_id,
            subject_id=subject_id,
            topic_id=topic_id,
            question_count=question_count
        )

        return jsonify(result), status_code

    except Exception as e:
        import traceback
        print(f"ERROR in start_test route: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Failed to start test: {str(e)}'
        }), 500

@tests_bp.route('/tests/<int:test_id>/submit', methods=['POST'])
def submit_test(test_id):
    """Submit complete test with all answers and optionally the test questions"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request data is required'
            }), 400

        answers = data.get('answers', [])
        test_questions = data.get('test_questions', None)  # Fresh questions from Azure OpenAI
        
        # Allow empty answers for auto-submit cases (all not attempted)
        # Validate answer format for any answers that are provided
        for answer in answers:
            if 'question_id' not in answer:
                return jsonify({
                    'success': False,
                    'message': 'Each answer must have question_id'
                }), 400

        result, status_code = test_service.submit_test(test_id, answers, test_questions)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to submit test: {str(e)}'
        }), 500

@tests_bp.route('/tests/<int:test_id>/status', methods=['GET'])
def get_test_status(test_id):
    """Get current test status and time remaining"""
    try:
        result, status_code = test_service.get_test_status(test_id)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get test status: {str(e)}'
        }), 500

@tests_bp.route('/tests/<int:test_id>/results', methods=['GET'])
def get_test_results(test_id):
    """Get detailed test results"""
    try:
        result, status_code = test_service.get_test_results(test_id)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get test results: {str(e)}'
        }), 500

@tests_bp.route('/tests/history', methods=['GET'])
@jwt_required()
def get_user_test_history():
    """Get user's test history"""
    try:
        user_id = get_jwt_identity()
        result, status_code = test_service.get_user_test_history(user_id)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get test history: {str(e)}'
        }), 500

@tests_bp.route('/tests/analytics', methods=['GET'])
@jwt_required()
def get_user_analytics():
    """Get user's performance analytics"""
    try:
        user_id = get_jwt_identity()
        result, status_code = test_service.get_user_analytics(user_id)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get analytics: {str(e)}'
        }), 500
