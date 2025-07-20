from flask import Blueprint, jsonify, request
from models.topic import Topic, NEET_TOPICS
from models.subject import Subject
from models.test import TestResult
from database.connection import db
from sqlalchemy import func

topics_bp = Blueprint('topics', __name__)

@topics_bp.route('/subjects/<int:subject_id>/topics', methods=['GET'])
def get_topics_by_subject(subject_id):
    """Get all topics for a specific subject"""
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({
                'success': False,
                'message': 'Subject not found'
            }), 404

        topics = Topic.query.filter_by(subject_id=subject_id).all()
        
        # If no topics in database, create default NEET topics
        if not topics and subject.name in NEET_TOPICS:
            for topic_data in NEET_TOPICS[subject.name]:
                topic = Topic(
                    name=topic_data['name'],
                    subject_id=subject_id,
                    description=topic_data['description']
                )
                db.session.add(topic)
            
            db.session.commit()
            topics = Topic.query.filter_by(subject_id=subject_id).all()

        topics_data = [topic.to_dict() for topic in topics]

        return jsonify({
            'success': True,
            'subject_name': subject.name,
            'topics': topics_data,
            'total_count': len(topics_data)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch topics: {str(e)}'
        }), 500

@topics_bp.route('/topics/<int:topic_id>', methods=['GET'])
def get_topic_details(topic_id):
    """Get detailed information about a specific topic"""
    try:
        topic = Topic.query.get(topic_id)
        if not topic:
            return jsonify({
                'success': False,
                'message': 'Topic not found'
            }), 404

        topic_data = topic.to_dict()
        
        # Add subject information
        subject = Subject.query.get(topic.subject_id)
        if subject:
            topic_data['subject_name'] = subject.name

        return jsonify({
            'success': True,
            'topic': topic_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch topic details: {str(e)}'
        }), 500

@topics_bp.route('/subjects/<int:subject_id>/topics', methods=['POST'])
def create_topic(subject_id):
    """Create a new topic for a subject"""
    try:
        # Verify subject exists
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({
                'success': False,
                'message': 'Subject not found'
            }), 404

        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'message': 'Topic name is required'
            }), 400

        # Check if topic already exists for this subject
        existing_topic = Topic.query.filter_by(
            name=data['name'],
            subject_id=subject_id
        ).first()
        
        if existing_topic:
            return jsonify({
                'success': False,
                'message': 'Topic already exists for this subject'
            }), 400

        # Create new topic
        topic = Topic(
            name=data['name'],
            subject_id=subject_id,
            description=data.get('description', '')
        )
        db.session.add(topic)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Topic created successfully',
            'topic': topic.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create topic: {str(e)}'
        }), 500

@topics_bp.route('/topics/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    """Update a topic"""
    try:
        topic = Topic.query.get(topic_id)
        if not topic:
            return jsonify({
                'success': False,
                'message': 'Topic not found'
            }), 404

        data = request.get_json()
        
        if 'name' in data:
            topic.name = data['name']
        if 'description' in data:
            topic.description = data['description']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Topic updated successfully',
            'topic': topic.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update topic: {str(e)}'
        }), 500

@topics_bp.route('/topics/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    """Delete a topic"""
    try:
        topic = Topic.query.get(topic_id)
        if not topic:
            return jsonify({
                'success': False,
                'message': 'Topic not found'
            }), 404

        db.session.delete(topic)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Topic deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete topic: {str(e)}'
        }), 500

@topics_bp.route('/topics/<int:topic_id>/stats', methods=['GET'])
def get_topic_stats(topic_id):
    """Get statistics for a specific topic"""
    try:
        topic = Topic.query.get(topic_id)
        if not topic:
            return jsonify({
                'success': False,
                'message': 'Topic not found'
            }), 404

        # Get test statistics for this topic
        total_tests = TestResult.query.filter_by(topic_id=topic_id).count()
        
        avg_score = db.session.query(func.avg(TestResult.score_percentage))\
            .filter_by(topic_id=topic_id).scalar() or 0

        return jsonify({
            'success': True,
            'stats': {
                'topic_name': topic.name,
                'total_questions': len(topic.questions),
                'total_tests_taken': total_tests,
                'average_score': round(avg_score, 2) if avg_score else 0
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch topic stats: {str(e)}'
        }), 500