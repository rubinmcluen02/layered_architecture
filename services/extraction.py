from datetime import datetime
from flask import session, abort
from extensions import db
from services.domain import Doctor, Appointment, Booking, Insurance, User
from services.exceptions import ExtractionError, check_service_status
from service_instances import *

class Extraction:
    def __init__(self):
        self.status = True 

    def start(self):
        self.status = True

    def stop(self):
        self.status = False

    def check_status(self):
        return self.status
    
    @check_service_status(ExtractionError)
    def get_user_id_from_session(self, default=1):
        return session.get('user_id', default)

    @check_service_status(ExtractionError)
    def get_appointments_by_user_id(self, user_id):
        try:
            return Appointment.query.filter_by(user_id=user_id).all()
        except Exception as e:
            raise ExtractionError(f"Error querying appointments: {e}")

    @check_service_status(ExtractionError)
    def view_user_appointments(self):
        user_id = self.get_user_id_from_session()
        appointments = self.get_appointments_by_user_id(user_id)
        return appointments
    
    @check_service_status(ExtractionError)
    def get_appointment_by_id(self, appointment_id):
        try:
            appointment = Appointment.query.get(appointment_id)
            if appointment is None:
                abort(404)
            return appointment
        except Exception as e:
            raise ExtractionError(f"Error fetching appointment: {e}")
        
    @check_service_status(ExtractionError)
    def get_insurance_by_id(self, insurance_id):
        try:
            insurance = Insurance.query.get(insurance_id)
            if not insurance:
                return None
            return insurance
        except Exception as e:
            raise ExtractionError(f"Error fetching insurance by ID: {e}")
        
    @check_service_status(ExtractionError)
    def get_booking_by_id(self, booking_id):
        try:
            booking = Booking.query.get_or_404(booking_id)
            return booking
        except Exception as e:
            raise ExtractionError(f"Error fetching booking by ID: {e}")
        
    @check_service_status(ExtractionError)
    def extract_login_credentials(self, form):
        username = form.get('username')
        password = form.get('password')
        return username, password
    
    @check_service_status(ExtractionError)
    def get_provider_record_by_username(self, username):
        conn = None
        cursor = None
        provider_record = None
        try:
            from service_instances import datastorage
            conn = datastorage.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            provider_record = cursor.fetchone()
        except Exception as e:
            print(f"Error fetching provider record: '{e}'")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return provider_record
 
    @check_service_status(ExtractionError)
    def add_user(self, username, hashed_password, user_type):
        self.check_status()
        try:
            new_user = User(username=username, password=hashed_password, user_type=user_type)
            db.session.add(new_user)
            db.session.commit()
            return new_user.id
        except Exception as e:
            db.session.rollback()
            print(f"Error adding user: '{e}'")
            return None

    @check_service_status(ExtractionError)
    def extract_registration_data(self, form):  
        registration_data = {
            'username': form.get('username'),
            'password': form.get('password'),
            'confirm_password': form.get('confirm_password'),
            'security_question': form.get('security_question'),
            'security_answer': form.get('security_answer'),
            'user_type': form.get('user_type', 'patient')
        }
        return registration_data
    
    @check_service_status(ExtractionError)
    def extract_username(self, form):
        username = form.get('username')
        return username

    @check_service_status(ExtractionError)
    def extract_change_password_data(self, form):
        data = {
            'answer': form.get('answer'),
            'new_password': form.get('new_password'),
            'confirm_new_password': form.get('confirm_new_password')
        }
        return data

    @check_service_status(ExtractionError)
    def get_user_security_question(self, username):
        try:
            from service_instances import datastorage
            conn = datastorage.get_db_connection()
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT u.id, u.username, sq.question_id 
                    FROM users u
                    JOIN security_questions sq ON u.id = sq.id 
                    WHERE u.username = %s
                """, (username,))
                result = cursor.fetchone()
            return result
        except Exception as e:
            print(f"Error fetching user security question: '{e}'")
            return None
        
    @check_service_status(ExtractionError)
    def verify_security_answer(self, id, answer):
        try:
            from service_instances import datastorage
            conn = datastorage.get_db_connection()
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT * FROM security_questions WHERE id = %s AND answer = %s', (id, answer))
                return bool(cursor.fetchone())
        except Exception as e:
            print(f"Error verifying security answer: '{e}'")
            return False

    @check_service_status(ExtractionError)
    def update_user_password(self, user_id, hashed_password):
        try:
            from service_instances import datastorage
            conn = datastorage.get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE users SET password = %s WHERE id = %s', (hashed_password, user_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error updating user password: '{e}'")
        finally:
            if conn and conn.is_connected():
                conn.close()

    @check_service_status(ExtractionError)
    def extract_booking_data(self, form):
        return {
            'patient_name': form.get('patient_name'),
            'doctor_name': form.get('doctor_name'),
            'date': form.get('date'),
            'time': form.get('time')
        }

    @check_service_status(ExtractionError)
    def extract_appointment_data(self, form, user_id):
        doctor_id = form.get('doctor_id')
        appointment_date = form.get('appointment_date')
        appointment_time = form.get('appointment_time')
        combined_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
        return Appointment(user_id=user_id, doctor_id=doctor_id, time=combined_datetime)

    @check_service_status(ExtractionError)
    def extract_appointment_update_data(self, form):
        new_date = form.get('date')
        new_time = form.get('time')
        new_datetime = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
        return new_datetime

    @check_service_status(ExtractionError)
    def extract_insurance_update_data(self, form):
        return {
            'name': form.get('name'),
            'policy_number': form.get('policy_number'),
            'address': form.get('address'),
            'phone': form.get('phone'),
            'copay': float(form.get('copay')) if form.get('copay') else None,
            'deductible': float(form.get('deductible')) if form.get('deductible') else None,
            'coinsurance': float(form.get('coinsurance')) if form.get('coinsurance') else None,
            'out_of_pocket_max': float(form.get('out_of_pocket_max')) if form.get('out_of_pocket_max') else None,
            'covered_services': form.get('covered_services')
        }
