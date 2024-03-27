from flask_sqlalchemy import SQLAlchemy
from extensions import db
from layers.exceptions import DataStorageError

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

def get_db_connection():
    try:
        import mysql.connector
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'password',
            'database': 'layered_architecture'
        }
        return mysql.connector.connect(**db_config)
    except Exception as e:
        raise DataStorageError from e
