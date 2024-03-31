from services.exceptions import AuthenticationError, check_service_status
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash


class Authentication:
    def __init__(self):
        self.app = None
        self.status = True

    def set_app(self, app):
        self.app = app

    def start(self):
        if self.app:
            self.app.config['AUTH_STATUS'] = True
            self.status = True

    def stop(self):
        if self.app:
            self.app.config['AUTH_STATUS'] = False
            self.status = False

    def check_status(self):
        if self.app:
            return self.app.config.get('AUTH_STATUS', True)
        return self.status


    @check_service_status(AuthenticationError)
    def authenticate_and_login(self, username, password, user_type):
        try:
            from service_instances import mapper

            user_record = mapper.get_user_by_username(username, user_type)
            if user_record:
                if check_password_hash(user_record.password, password):
                    login_user(user_record, remember=True)
                    return True
            return False

        except Exception as e:
            raise e

    
    @check_service_status(AuthenticationError)
    def perform_logout(self):
        logout_user()