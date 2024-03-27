from werkzeug.security import check_password_hash
from flask_login import login_user
from layers.extraction import get_user_by_username
from layers.mapper import map_user_record_to_user

def authenticate_and_login(username, password, user_type):
    user_record = get_user_by_username(username, user_type)
    if user_record:
        if check_password_hash(user_record['password'], password):
            user = map_user_record_to_user(user_record)
            login_user(user, remember=True)
            return True
    return False
