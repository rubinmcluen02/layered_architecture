from layers.domain import User

def map_user_record_to_user(user_record):
    if user_record:
        return User(id=user_record['id'], username=user_record['username'], user_type=user_record.get('user_type'))
    return None
