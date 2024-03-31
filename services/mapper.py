from services.domain import User
from services.exceptions import MapperError, check_service_status

class Mapper:
    def __init__(self):
        self.status = True

    def start(self):
        self.status = True

    def stop(self):
        self.status = False

    def check_status(self):
        return self.status

    @check_service_status(MapperError)
    def map_user_record_to_user(self, user_record):
        try:
            if user_record:
                return User(id=user_record['id'],
                            username=user_record['username'],
                            password=user_record.get('password'),
                            user_type=user_record.get('user_type'))
            return None
        except Exception as e:
            raise MapperError from e


    @check_service_status(MapperError)
    def get_user_by_username(self, username, user_type):
        conn = None
        try:
            from service_instances import datastorage
            conn = datastorage.get_db_connection()
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT * FROM users WHERE username = %s AND user_type = %s', (username, user_type))
                user_record = cursor.fetchone()
                return self.map_user_record_to_user(user_record)
        except Exception as e:
            raise MapperError(f"Error fetching user by username: {e}")
        finally:
            if conn:
                conn.close()

    @check_service_status(MapperError)
    def get_user_by_id(self, user_id):
        conn = None
        try:
            from service_instances import datastorage
            conn = datastorage.get_db_connection()
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT id, username, user_type FROM users WHERE id = %s', (user_id,))
                user_record = cursor.fetchone()
                return self.map_user_record_to_user(user_record)
        except Exception as e:
            raise MapperError(f"Error fetching user by ID: {e}")
        finally:
            if conn:
                conn.close()
