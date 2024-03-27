import re

from layers.exceptions import ValidationError

def validate_password(password, confirm_password):
    try:
        if password != confirm_password:
            return False, 'Passwords do not match'

        if len(password) < 5:
            return False, 'Password must be at least 5 characters long'

        if not re.search('[A-Z]', password):
            return False, 'Password must contain at least one uppercase letter'

        if not re.search('[0-9]', password):
            return False, 'Password must contain at least one number'

        return True, ''
    except Exception as e:
        raise ValidationError from e

def get_question_text_by_id(question_id):
    try:
        questions = {
            1: "What was the name of your first pet?",
            2: "What is your mother's maiden name?",
            3: "What was the make and model of your first car?",
            4: "In what city were you born?",
            5: "What is your favorite movie?",
        }
        return questions.get(question_id, "Question not available")
    except Exception as e:
        raise ValidationError from e
