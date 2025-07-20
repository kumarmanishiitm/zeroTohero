from flask import Blueprint, jsonify, request
from models.subject import Subject, NEET_SUBJECTS
from database.connection import db

subjects_bp = Blueprint('subjects', __name__)

@subjects_bp.route('/subjects', methods=['GET'])
def get_subjects():
    """Get all available subjects"""
    try:
        # Query only active subjects
        subjects = Subject.query.filter_by(is_active=True).all()
        
        # If no subjects in database, create default NEET subjects
        if not subjects:
            for subject_data in NEET_SUBJECTS:
                subject = Subject(
                    name=subject_data['name'],
                    description=subject_data['description'],
                    is_active=True
                )
                db.session.add(subject)
            
            db.session.commit()
            subjects = Subject.query.filter_by(is_active=True).all()
        
        subjects_data = [subject.to_dict() for subject in subjects]
        
        return jsonify({
            'success': True,
            'subjects': subjects_data,
            'total_count': len(subjects_data)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch subjects: {str(e)}'
        }), 500

@subjects_bp.route('/subjects/<int:subject_id>', methods=['GET'])
def get_subject_details(subject_id):
    """Get detailed information about a specific subject"""
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({
                'success': False,
                'message': 'Subject not found'
            }), 404

        subject_data = subject.to_dict()
        subject_data['topics'] = subject.get_topics()

        return jsonify({
            'success': True,
            'subject': subject_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch subject details: {str(e)}'
        }), 500

@subjects_bp.route('/subjects', methods=['POST'])
def create_subject():
    """Create a new subject"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'message': 'Subject name is required'
            }), 400

        # Check if subject already exists
        existing_subject = Subject.query.filter_by(name=data['name']).first()
        if existing_subject:
            return jsonify({
                'success': False,
                'message': 'Subject already exists'
            }), 400

        # Create new subject
        subject = Subject(
            name=data['name'],
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        db.session.add(subject)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Subject created successfully',
            'subject': subject.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create subject: {str(e)}'
        }), 500

@subjects_bp.route('/subjects/<int:subject_id>/stats', methods=['GET'])
def get_subject_stats(subject_id):
    """Get statistics for a specific subject"""
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({
                'success': False,
                'message': 'Subject not found'
            }), 404

        from src.models.test import TestResult
        from sqlalchemy import func

        # Get test statistics
        total_tests = TestResult.query.filter_by(subject_id=subject_id).count()
        
        avg_score = db.session.query(func.avg(TestResult.score_percentage))\
            .filter_by(subject_id=subject_id).scalar() or 0

        return jsonify({
            'success': True,
            'stats': {
                'subject_name': subject.name,
                'total_topics': len(subject.topics),
                'total_questions': len(subject.questions),
                'total_tests_taken': total_tests,
                'average_score': round(avg_score, 2) if avg_score else 0
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch subject stats: {str(e)}'
        }), 500