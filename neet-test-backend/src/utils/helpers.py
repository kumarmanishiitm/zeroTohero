def generate_question(subject, topic):
    # Placeholder function to generate a question based on subject and topic
    return {
        "question": f"What is a question about {topic} in {subject}?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "Option A",
        "explanation": f"This is an explanation for the question about {topic} in {subject}."
    }

def calculate_score(correct_answers, total_questions):
    if total_questions == 0:
        return 0
    return (correct_answers / total_questions) * 100

def format_results(score):
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 50:
        return "Average"
    else:
        return "Needs Improvement"