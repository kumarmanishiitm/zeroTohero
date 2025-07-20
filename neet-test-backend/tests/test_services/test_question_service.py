from src.services.question_service import QuestionService
import unittest

class TestQuestionService(unittest.TestCase):

    def setUp(self):
        self.question_service = QuestionService()

    def test_generate_question_valid_subject(self):
        subject = 'Physics'
        topic = 'Kinematics'
        question = self.question_service.generate_question(subject, topic)
        self.assertIsNotNone(question)
        self.assertIn('question_text', question)
        self.assertIn('options', question)
        self.assertIn('correct_answer', question)

    def test_generate_question_invalid_subject(self):
        subject = 'InvalidSubject'
        topic = 'Kinematics'
        with self.assertRaises(ValueError):
            self.question_service.generate_question(subject, topic)

    def test_generate_question_valid_topic(self):
        subject = 'Biology'
        topic = 'Cell Biology'
        question = self.question_service.generate_question(subject, topic)
        self.assertIsNotNone(question)

    def test_get_explanation(self):
        question_id = 1  # Assuming a valid question ID
        explanation = self.question_service.get_explanation(question_id)
        self.assertIsNotNone(explanation)

if __name__ == '__main__':
    unittest.main()