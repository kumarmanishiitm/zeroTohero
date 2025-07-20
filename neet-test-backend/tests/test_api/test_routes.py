from flask import Flask, jsonify
from flask_testing import TestCase
from src.api.routes import auth, subjects, topics, questions, tests

class TestRoutes(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.register_blueprint(auth.bp)
        app.register_blueprint(subjects.bp)
        app.register_blueprint(topics.bp)
        app.register_blueprint(questions.bp)
        app.register_blueprint(tests.bp)
        return app

    def test_auth_routes(self):
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)

    def test_subjects_routes(self):
        response = self.client.get('/subjects')
        self.assertEqual(response.status_code, 200)

    def test_topics_routes(self):
        response = self.client.get('/topics/1')  # Assuming 1 is a valid subject ID
        self.assertEqual(response.status_code, 200)

    def test_questions_routes(self):
        response = self.client.get('/questions?subject_id=1&topic_id=1')  # Assuming valid IDs
        self.assertEqual(response.status_code, 200)

    def test_tests_routes(self):
        response = self.client.post('/tests', json={'answers': []})  # Assuming empty answers for testing
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    import unittest
    unittest.main()