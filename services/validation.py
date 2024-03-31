import re
from services.exceptions import ValidationError, check_service_status

class Validation:
    def __init__(self):
        self.status = True

    def start(self):
        self.status = True

    def stop(self):
        self.status = False

    def check_status(self):
        return self.status

    @check_service_status(ValidationError)
    def validate_password(self, password, confirm_password):
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
            raise e

    @check_service_status(ValidationError)
    def get_question_text_by_id(self, question_id):
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
            raise e
        
    @check_service_status(ValidationError)
    def validate_registration_form(self, form):
        username = form.get('username')
        password = form.get('password')
        confirm_password = form.get('confirm_password')
        email = form.get('email')

        errors = {}
        if not username:
            errors['username'] = 'Username is required'

        password_valid, password_error = self.validate_password(password, confirm_password)
        if not password_valid:
            errors['password'] = password_error

        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors['email'] = 'Invalid email format'

        return len(errors) == 0, errors

    @check_service_status(ValidationError)
    def validate_login_credentials(self, username, password):
            errors = {}

            if not username:
                errors['username'] = 'Username is required.'

            if not password:
                errors['password'] = 'Password is required.'

            return len(errors) == 0, errors