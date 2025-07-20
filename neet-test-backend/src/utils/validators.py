def validate_subject(subject):
    valid_subjects = ['Physics', 'Chemistry', 'Biology']
    if subject not in valid_subjects:
        raise ValueError(f"Invalid subject: {subject}. Must be one of {valid_subjects}.")
    return True

def validate_topic(topic, subject):
    valid_topics = {
        'Physics': ['Mechanics', 'Optics', 'Thermodynamics'],
        'Chemistry': ['Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry'],
        'Biology': ['Cell Biology', 'Genetics', 'Ecology']
    }
    if subject not in valid_topics or topic not in valid_topics[subject]:
        raise ValueError(f"Invalid topic: {topic} for subject: {subject}.")
    return True

def validate_answer(answer, correct_answer):
    if answer != correct_answer:
        raise ValueError("Incorrect answer.")
    return True

def validate_user_input(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a dictionary.")
    required_fields = ['subject', 'topic', 'answer']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}.")
    return True