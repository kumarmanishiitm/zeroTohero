from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from database.connection import db

# Create the auth blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/quick-login', methods=['POST'])
def quick_login():
    """Quick login without password for testing"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request data is required'
            }), 400

        username = data.get('username')

        if not username:
            return jsonify({
                'success': False,
                'message': 'Username is required'
            }), 400

        # Find or create user
        user = User.query.filter_by(username=username).first()
        
        if not user:
            # Create new user for quick login
            user = User(
                username=username,
                email=f"{username}@neettest.com"
            )
            user.set_password("neet123")  # Default password for quick login
            
            db.session.add(user)
            db.session.commit()

        # Create access token
        access_token = create_access_token(identity=user.id)

        return jsonify({
            'success': True,
            'message': 'Quick login successful',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Quick login failed: {str(e)}'
        }), 500

@auth_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get user: {str(e)}'
        }), 500
