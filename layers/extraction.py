from extensions import db
from layers.data_storage import get_db_connection, Doctor
from layers.exceptions import ExtractionError

def insert_doctor_data():
    try:
        if Doctor.query.first() is None:
            doctors_data = [
                {"id": 1, "name": "Dr. Alice Smith", "address": "123 Healing Blvd", "specialization": "Cardiology"},
                {"id": 2, "name": "Dr. Bob Johnson", "address": "234 Care Lane", "specialization": "Dermatology"},
                {"id": 3, "name": "Dr. Carol Davis", "address": "345 Wellness Drive", "specialization": "Pediatrics"},
                {"id": 4, "name": "Dr. David Williams", "address": "456 Health Way", "specialization": "Neurology"},
                {"id": 5, "name": "Dr. Emily Brown", "address": "567 Recovery Road", "specialization": "Orthopedics"}
            ]

            for doctor_data in doctors_data:
                doctor = Doctor(**doctor_data)
                db.session.add(doctor)

            db.session.commit()
            print("Inserted doctor data into the database.")
        else:
            print("Doctor table is not empty, no data inserted.")
    except Exception as e:
        raise ExtractionError from e

def get_user_by_username(username, user_type):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM users WHERE username = %s AND user_type = %s', (username, user_type))
        user_record = cursor.fetchone()

        cursor.close()
        conn.close()
        return user_record
    except Exception as e:
        raise ExtractionError from e

def get_user_by_id(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, username, user_type FROM users WHERE id = %s", (user_id,))
        user_record = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return user_record
    except Exception as e:
        raise ExtractionError from e

