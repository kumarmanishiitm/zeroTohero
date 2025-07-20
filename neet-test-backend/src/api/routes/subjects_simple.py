from flask import Blueprint, jsonify, request
from models.subject import Subject, NEET_SUBJECTS
from database.connection import db

subjects_bp = Blueprint('subjects', __name__)

@subjects_bp.route('/subjects', methods=['GET'])
def get_subjects():
    """Get all available subjects"""
    try:
        subjects = Subject.query.all()
        
        # If no subjects in database, create default NEET subjects
        if not subjects:
            for subject_data in NEET_SUBJECTS:
                subject = Subject(
                    name=subject_data['name'],
                    description=subject_data['description']
                )
                db.session.add(subject)
            
            db.session.commit()
            subjects = Subject.query.all()
        
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

        return jsonify({
            'success': True,
            'subject': subject.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch subject details: {str(e)}'
        }), 500
