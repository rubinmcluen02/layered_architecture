from extensions import db
from flask_login import UserMixin
from services.exceptions import DomainError, check_service_status

class Domain:
    def __init__(self):
        self.status = True

    def start(self):
        self.status = True

    def stop(self):
        self.status = False

    def check_status(self):
        return self.status

    @check_service_status(DomainError)
    def create_user(self, username, password, user_type):
        try:
            user = User(username=username, password=password, user_type=user_type)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            raise DomainError from e
        
    @check_service_status(DomainError)
    def add_to_db(self, obj):
        try:
            db.session.add(obj)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise DomainError(f"Error adding object to DB: {e}")

    @check_service_status(DomainError)
    def delete_from_db(self, obj):
        try:
            db.session.delete(obj)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise DomainError(f"Error deleting object from DB: {e}")

    @check_service_status(DomainError)
    def insert_doctor_data(self):
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
                self.add_to_db(doctor)

            print("Inserted doctor data into the database.")
        else:
            print("Doctor table is not empty, no data inserted.")

    @check_service_status(DomainError)
    def create_user(self, username, hashed_password, security_question, security_answer, user_type):
        try:
            new_user = User(username=username, password=hashed_password, user_type=user_type)
            self.add_to_db(new_user)
            db.session.flush() 
            self.add_security_question(new_user.id, security_question, security_answer)
            db.session.commit()
            return new_user.id
        except Exception as e:
            db.session.rollback()
            raise DomainError(f"Error creating user: '{e}'")

    @check_service_status(DomainError)
    def add_security_question(self, id, question_id, answer):
        self.check_status()
        insert_security_question_query = """
        INSERT INTO security_questions (id, question_id, answer) VALUES (%s, %s, %s)
        """
        conn = None
        try:
            from service_instances import datastorage
            conn = datastorage.get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(insert_security_question_query, (id, question_id, answer))
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error adding security question: '{e}'")
        finally:
            if conn and conn.is_connected():
                conn.close()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(50))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100))
    doctor_name = db.Column(db.String(100))
    date = db.Column(db.String(10))  # String for simplicity
    time = db.Column(db.String(8))  # String for simplicity

class Insurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    policy_number = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(100), nullable=False)  # Non-modifiable
    address = db.Column(db.String(200))
    phone = db.Column(db.String(100))
    copay = db.Column(db.Float)
    deductible = db.Column(db.Float)
    coinsurance = db.Column(db.Float)
    out_of_pocket_max = db.Column(db.Float)
    covered_services = db.Column(db.Text)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    user = db.relationship('User', backref='appointments', lazy=True)
    doctor = db.relationship('Doctor', backref='appointments', lazy=True)