from src.models.question import Question
import pytest

@pytest.fixture
def question():
    return Question(
        question_text="What is the powerhouse of the cell?",
        options=["Nucleus", "Mitochondria", "Ribosome", "Endoplasmic Reticulum"],
        correct_answer="Mitochondria",
        explanation="Mitochondria are known as the powerhouse of the cell because they produce ATP, the energy currency of the cell."
    )

def test_question_creation(question):
    assert question.question_text == "What is the powerhouse of the cell?"
    assert question.options == ["Nucleus", "Mitochondria", "Ribosome", "Endoplasmic Reticulum"]
    assert question.correct_answer == "Mitochondria"
    assert question.explanation == "Mitochondria are known as the powerhouse of the cell because they produce ATP, the energy currency of the cell."

def test_is_answer_correct(question):
    assert question.is_answer_correct("Mitochondria") is True
    assert question.is_answer_correct("Nucleus") is False

def test_get_explanation(question):
    assert question.get_explanation() == question.explanation