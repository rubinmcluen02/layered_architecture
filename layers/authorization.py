from flask import Blueprint, request, redirect, render_template, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import urllib.parse

from layers.domain import User
from layers.extraction import get_user_by_username, get_db_connection
from layers.authentication import authenticate_and_login
from layers.validation import get_question_text_by_id, validate_password
from extensions import login_manager
from layers.data_storage import *

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate_and_login(username, password, 'patient'):
            return redirect(url_for('auth.patient_dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('patient_login.html')

@auth_blueprint.route('/provider_login', methods=['GET', 'POST'])
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
                    return redirect(url_for('auth.staff_dashboard'))
                elif user_type == "doctor":
                    return redirect(url_for('auth.doctor_dashboard'))
                elif user_type == "admin":
                    return redirect(url_for('auth.admin_dashboard'))
            else:
                flash('Invalid username or password')
    
    return render_template('provider_login.html')

@auth_blueprint.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))

@auth_blueprint.route('/')
def home():
    return render_template('welcome.html')

@auth_blueprint.route('/staff_dashboard')
@login_required
def staff_dashboard():
    if current_user.user_type != 'staff':
        return unauthorized_callback()
    return render_template('staff_dashboard.html', login_success=True)

@auth_blueprint.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.user_type != 'admin':
        return unauthorized_callback()
    return render_template('admin_dashboard.html', login_success=True)

@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('You must be logged in to view this page.')
    return redirect(url_for('home'))

@auth_blueprint.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('auth.patient_login'))

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

@auth_blueprint.route('/change_password', methods=['GET'])
def change_password():
    return render_template('request_username.html')

@auth_blueprint.route('/verify_username', methods=['POST'])
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
        return redirect(url_for('auth.change_password'))

@auth_blueprint.route('/change_password_final', methods=['POST'])
def change_password_final():
    answer = request.form['answer']
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_new_password']

    if new_password != confirm_new_password:
        flash('New passwords do not match.')
        return redirect(url_for('auth.verify_username'))

    user_id = session.get('user_id')
    if not user_id:
        flash('User session expired or invalid. Please start the process again.')
        return redirect(url_for('auth.change_password'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM security_questions WHERE id = %s AND answer = %s', (user_id, answer))
    if not cursor.fetchone():
        flash('Incorrect answer to security question.')
        return redirect(url_for('auth.verify_username'))

    hashed_password = generate_password_hash(new_password)
    cursor.execute('UPDATE users SET password = %s WHERE id = %s', (hashed_password, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    session.pop('user_id', None)
    flash('Your password has been updated successfully.')
    return redirect(url_for('auth.patient_login'))


@auth_blueprint.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.user_type != 'doctor':
        return unauthorized_callback()
    bookings = Booking.query.all()
    return render_template('index.html', bookings=bookings)

@auth_blueprint.route('/add_booking', methods=['POST'])
@login_required
def add_booking():
    patient_name = request.form['patient_name']
    doctor_name = request.form['doctor_name']
    date = request.form['date']
    time = request.form['time']
    
    new_booking = Booking(patient_name=patient_name, doctor_name=doctor_name, date=date, time=time)
    db.session.add(new_booking)
    db.session.commit()
    
    return redirect(url_for('auth.doctor_dashboard'))

@auth_blueprint.route('/delete_booking/<int:id>', methods=['POST'])
@login_required
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    db.session.delete(booking)
    db.session.commit()
    return redirect(url_for('auth.doctor_dashboard'))

@auth_blueprint.route('/update_booking/<int:id>', methods=['POST'])
@login_required
def update_booking(id):
    booking = Booking.query.get_or_404(id)
    booking.patient_name = request.form['patient_name']
    booking.doctor_name = request.form['doctor_name']
    booking.date = request.form['date']
    booking.time = request.form['time']
    db.session.commit()
    return redirect(url_for('auth.doctor_dashboard'))

@auth_blueprint.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.user_type != 'patient':
        return unauthorized_callback()
    return render_template('patient_dashboard.html', login_success=True)

@auth_blueprint.route('/book-appointment', methods=['GET', 'POST'])
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
        return redirect(url_for('auth.view_appointments'))
    else:
        doctors = Doctor.query.all()
        return render_template('book_appointment.html', doctors=doctors)
    
@auth_blueprint.route('/change-appointment/<int:appointment_id>', methods=['GET', 'POST'])
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

        return redirect(url_for('auth.view_appointments'))
    else:
        return render_template('change_appointment.html', appointment=appointment)

@auth_blueprint.route('/update-insurance', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.patient_dashboard'))

    # Return the template with insurance information for both 'GET' and 'POST' requests
    return render_template('update_insurance.html', insurance=insurance)

@auth_blueprint.route('/view-appointments')
@login_required
def view_appointments():
    user_id = session.get('user_id', 1)  
    appointments = Appointment.query.filter_by(user_id=user_id).all()
    return render_template('view_appointments.html', appointments=appointments)

@auth_blueprint.route('/cancel-appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('auth.view_appointments'))

@auth_blueprint.route('/modify-appointment/<int:appointment_id>', methods=['GET'])
@login_required
def modify_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('change_appointment.html', appointment=appointment)

