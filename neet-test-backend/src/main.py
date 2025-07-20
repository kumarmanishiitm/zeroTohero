from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
import sys

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import db, init_db
from config.settings import DevelopmentConfig

# Import route blueprints
from api.routes.auth import auth_bp
from api.routes.subjects import subjects_bp
from api.routes.topics import topics_bp
from api.routes.questions import questions_bp
from api.routes.tests import tests_bp

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(DevelopmentConfig)
    
    # Enable CORS for all routes
    CORS(app, origins=["*"], supports_credentials=True)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(subjects_bp, url_prefix='/api/v1')
    app.register_blueprint(topics_bp, url_prefix='/api/v1')
    app.register_blueprint(questions_bp, url_prefix='/api/v1')
    app.register_blueprint(tests_bp, url_prefix='/api/v1')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'NEET Test Backend API is running',
            'version': '1.0.0'
        }), 200
    
    # API documentation endpoint
    @app.route('/api/v1', methods=['GET'])
    def api_info():
        return jsonify({
            'message': 'NEET Test Backend API v1.0',
            'description': 'Medical NEET examination preparation platform',
            'endpoints': {
                'subjects': '/api/v1/subjects',
                'topics': '/api/v1/subjects/{id}/topics',
                'questions': '/api/v1/questions/*',
                'tests': '/api/v1/tests/*'
            },
            'features': [
                'User registration and authentication',
                'Subject and topic management',
                'Question generation and evaluation',
                'Test management and scoring',
                'Performance analytics',
                'Leaderboard system'
            ]
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Endpoint not found',
            'error': 'Not Found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'message': 'Method not allowed for this endpoint',
            'error': 'Method Not Allowed'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': 'Internal Server Error'
        }), 500
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token has expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Invalid token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Authentication token required'
        }), 401
    
    # Create database tables and initial data
    with app.app_context():
        db.create_all()
        create_initial_data()
    
    return app

def create_initial_data():
    """Create initial data if database is empty"""
    try:
        from models.subject import Subject, NEET_SUBJECTS
        from models.topic import Topic, NEET_TOPICS
        
        # Create subjects if they don't exist
        if Subject.query.count() == 0:
            for subject_data in NEET_SUBJECTS:
                subject = Subject(
                    name=subject_data['name'],
                    description=subject_data['description']
                )
                db.session.add(subject)
            db.session.commit()
            print("✓ Created initial subjects")
        
        # Create topics if they don't exist
        if Topic.query.count() == 0:
            subjects = Subject.query.all()
            subject_map = {s.name: s.id for s in subjects}
            
            for subject_name, topics_data in NEET_TOPICS.items():
                if subject_name in subject_map:
                    subject_id = subject_map[subject_name]
                    for topic_data in topics_data:
                        topic = Topic(
                            name=topic_data['name'],
                            subject_id=subject_id,
                            description=topic_data['description']
                        )
                        db.session.add(topic)
            db.session.commit()
            print("✓ Created initial topics")
            
    except Exception as e:
        print(f"Error creating initial data: {e}")
        db.session.rollback()
app = create_app()

if __name__ == '__main__':
    # Development server configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"""
🚀 NEET Test Backend API Starting...

📚 Features:
   • User Authentication & Registration
   • Subject Management (Physics, Chemistry, Biology)
   • Topic-based Question Generation
   • Interactive Test Interface
   • Performance Analytics & Scoring
   • Leaderboard System

🌐 Endpoints:
   • Health Check: http://localhost:{port}/health
   • API Info: http://localhost:{port}/api/v1
   • Documentation: See README.md

🔧 Environment: {'Development' if debug else 'Production'}
""")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
