import mysql.connector
from mysql.connector import Error
from flask_login import login_user, LoginManager, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, redirect, render_template, url_for, flash, session
import re
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import urllib.parse

app = Flask(__name__)
app.secret_key = 'secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

password = "password"
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password}@localhost/layered_architecture'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)

# Domain Layer
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
    date = db.Column(db.String(10))  # String for simplicity in this example
    time = db.Column(db.String(8))   # String for simplicity in this example
    
class Insurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    policy_number = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(100), nullable=False)  # Date of birth is not modifiable
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
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('appointments', lazy=True))

with app.app_context():
    db.create_all()
    
def insert_doctor_data():
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

with app.app_context():
    insert_doctor_data()

    
    
    
    
####################################

# Rubin
# Authorization and Authentication

####################################

# Data Storage Layer
def get_db_connection():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'layered_architecture'
    }
    return mysql.connector.connect(**db_config)

# Extraction Layer
def get_user_by_username(username, user_type):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM users WHERE username = %s AND user_type = %s', (username, user_type))
    user_record = cursor.fetchone()

    cursor.close()
    conn.close()
    return user_record

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, username, user_type FROM users WHERE id = %s", (user_id,))
    user_record = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return user_record

# Mapper Layer
def map_user_record_to_user(user_record):
    if user_record:
        return User(id=user_record['id'], username=user_record['username'], user_type=user_record.get('user_type'))
    return None

#Authentication Layer
def authenticate_and_login(username, password, user_type):
    user_record = get_user_by_username(username, user_type)
    if user_record:
        if check_password_hash(user_record['password'], password):
            user = map_user_record_to_user(user_record)
            login_user(user, remember = True)
            return True
    return False

# Validation Layer
def validate_password(password, confirm_password):
    if password != confirm_password:
        return False, 'Passwords do not match'

    if len(password) < 5:
        return False, 'Password must be at least 5 characters long'

    if not re.search('[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'

    if not re.search('[0-9]', password):
        return False, 'Password must contain at least one number'

    return True, ''

def get_question_text_by_id(question_id):
    questions = {
        1: "What was the name of your first pet?",
        2: "What is your mother's maiden name?",
        3: "What was the make and model of your first car?",
        4: "In what city were you born?",
        5: "What is your favorite movie?",
    }
    return questions.get(question_id, "Question not available")

# Routes
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Authorization Layer
@app.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate_and_login(username, password, 'patient'):
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('patient_login.html')

@app.route('/provider_login', methods=['GET', 'POST'])
def provider_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        provider_record = cursor.fetchone()
        cursor.close()
        conn.close()

        if provider_record:
            user_type = provider_record['user_type']
            if authenticate_and_login(username, password, user_type):
                user = User(id=provider_record['id'], username=username, user_type=user_type)
                login_user(user)
                
                if user_type == "staff":
                    return redirect(url_for('staff_dashboard'))
                elif user_type == "doctor":
                    return redirect(url_for('doctor_dashboard'))
                elif user_type == "admin":
                    return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid username or password')
    
    return render_template('provider_login.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/staff_dashboard')
@login_required
def staff_dashboard():
    if current_user.user_type != 'staff':
        return unauthorized_callback()
    return render_template('staff_dashboard.html', login_success=True)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.user_type != 'admin':
        return unauthorized_callback()
    return render_template('admin_dashboard.html', login_success=True)

@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('You must be logged in to view this page.')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        security_question = request.form['security_question']
        security_answer = request.form['security_answer']
        user_type = request.form.get('user_type', 'patient')

        valid, error_message = validate_password(password, confirm_password)
        if not valid:
            flash(error_message)
            return render_template('register.html')
        
        existing_user = get_user_by_username(username, user_type)
        if existing_user:
            flash('Username already taken. Please choose another.')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        create_user(username, hashed_password, security_question, security_answer, user_type)
        flash('Registration successful. Please log in.')
        return redirect(url_for('patient_login'))

    return render_template('register.html')

def create_user(username, hashed_password, security_question, security_answer, user_type):
    insert_user_query = """
    INSERT INTO users (username, password, user_type)
    VALUES (%s, %s, %s)
    """

    insert_security_question_query = """
    INSERT INTO security_questions (id, question_id, answer) VALUES (%s, %s, %s)
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(insert_user_query, (username, hashed_password, user_type))
        id = cursor.lastrowid
        cursor.execute(insert_security_question_query, (id, security_question, security_answer))
        conn.commit()

    except Error as e:
        print(f"Error: '{e}'")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection is closed")

@app.route('/change_password', methods=['GET'])
def change_password():
    return render_template('request_username.html')

@app.route('/verify_username', methods=['POST'])
def verify_username():
    username = request.form['username']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT u.id, u.username, sq.question_id 
        FROM users u
        JOIN security_questions sq ON u.id = sq.id 
        WHERE u.username = %s
    """, (username,))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        session['user_id'] = result['id']
        question_text = get_question_text_by_id(result['question_id'])
        return render_template('answer_security_question.html', question=question_text)
    else:
        flash('Username not found or no security question set for this user.')
        return redirect(url_for('change_password'))

@app.route('/change_password_final', methods=['POST'])
def change_password_final():
    answer = request.form['answer']
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_new_password']

    if new_password != confirm_new_password:
        flash('New passwords do not match.')
        return redirect(url_for('verify_username'))

    user_id = session.get('user_id')
    if not user_id:
        flash('User session expired or invalid. Please start the process again.')
        return redirect(url_for('change_password'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM security_questions WHERE id = %s AND answer = %s', (user_id, answer))
    if not cursor.fetchone():
        flash('Incorrect answer to security question.')
        return redirect(url_for('verify_username'))

    hashed_password = generate_password_hash(new_password)
    cursor.execute('UPDATE users SET password = %s WHERE id = %s', (hashed_password, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    session.pop('user_id', None)
    flash('Your password has been updated successfully.')
    return redirect(url_for('patient_login'))


    
    
###############################
    
# Subasree
# Provider Functions

###############################

encoded_password = urllib.parse.quote_plus(password)

#old sql db
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
#new sql db

@app.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.user_type != 'doctor':
        return unauthorized_callback()
    bookings = Booking.query.all()
    return render_template('index.html', bookings=bookings)

@app.route('/add_booking', methods=['POST'])
@login_required
def add_booking():
    patient_name = request.form['patient_name']
    doctor_name = request.form['doctor_name']
    date = request.form['date']
    time = request.form['time']
    
    new_booking = Booking(patient_name=patient_name, doctor_name=doctor_name, date=date, time=time)
    db.session.add(new_booking)
    db.session.commit()
    
    return redirect(url_for('doctor_dashboard'))

@app.route('/delete_booking/<int:id>', methods=['POST'])
@login_required
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    db.session.delete(booking)
    db.session.commit()
    return redirect(url_for('doctor_dashboard'))

@app.route('/update_booking/<int:id>', methods=['POST'])
@login_required
def update_booking(id):
    booking = Booking.query.get_or_404(id)
    booking.patient_name = request.form['patient_name']
    booking.doctor_name = request.form['doctor_name']
    booking.date = request.form['date']
    booking.time = request.form['time']
    db.session.commit()
    return redirect(url_for('doctor_dashboard'))

'''
# Original password with "@" symbol
password = "password@123"

# Encoded password
encoded_password = urllib.parse.quote_plus(password)

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{encoded_password}@localhost/user_test'
'''



#################################

# Veetrag
# Patient Functions

#################################

# Routes
# @app.route('/')
# def home():
#     # Dummy user logged in
#     user_id = session.get('user_id', 1)  # Default to 1 for example purposes
#     return render_template('home.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # Dummy login implementation
#     if request.method == 'POST':
#         session['user_id'] = 1  # Normally you would verify the username and password
#         return redirect(url_for('home'))
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     return redirect(url_for('home'))

@app.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.user_type != 'patient':
        return unauthorized_callback()
    return render_template('patient_dashboard.html', login_success=True)

@app.route('/book-appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        combined_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
        user_id = session.get('id', 1) 
        appointment = Appointment(user_id=user_id, doctor_id=doctor_id, time=combined_datetime)
        db.session.add(appointment)
        db.session.commit()
        return redirect(url_for('view_appointments'))
    else:
        doctors = Doctor.query.all()
        return render_template('book_appointment.html', doctors=doctors)
    
@app.route('/change-appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def change_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    if request.method == 'POST':
        new_date = request.form['date']
        new_time = request.form['time']

        # Convert new_date and new_time to a datetime object
        new_datetime = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")

        # Update the appointment with the new date and time
        appointment.time = new_datetime
        db.session.commit()

        return redirect(url_for('view_appointments'))
    else:
        return render_template('change_appointment.html', appointment=appointment)

@app.route('/update-insurance', methods=['GET', 'POST'])
@login_required
def update_insurance():
    insurance_id = 1  # Placeholder for actual insurance ID retrieval logic
    insurance = Insurance.query.get(insurance_id)

    if request.method == 'POST':
        if insurance:
            insurance.name = request.form['name']
            insurance.policy_number = request.form['policy_number']
            # DOB is not updated since it's not modifiable
            insurance.address = request.form['address']
            insurance.phone = request.form['phone']
            insurance.copay = float(request.form['copay']) if request.form['copay'] else None
            insurance.deductible = float(request.form['deductible']) if request.form['deductible'] else None
            insurance.coinsurance = float(request.form['coinsurance']) if request.form['coinsurance'] else None
            insurance.out_of_pocket_max = float(request.form['out_of_pocket_max']) if request.form['out_of_pocket_max'] else None
            insurance.covered_services = request.form['covered_services']
            
            db.session.commit()
            return redirect(url_for('patient_dashboard'))

    # Return the template with insurance information for both 'GET' and 'POST' requests
    return render_template('update_insurance.html', insurance=insurance)

@app.route('/view-appointments')
@login_required
def view_appointments():
    user_id = session.get('user_id', 1)  
    appointments = Appointment.query.filter_by(user_id=user_id).all()
    return render_template('view_appointments.html', appointments=appointments)

@app.route('/cancel-appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('view_appointments'))

@app.route('/modify-appointment/<int:appointment_id>', methods=['GET'])
@login_required
def modify_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('change_appointment.html', appointment=appointment)

