from flask import Blueprint, request, redirect, render_template, url_for, flash, session
from flask_login import login_required, current_user
from services.exceptions import *
from werkzeug.security import generate_password_hash
from extensions import login_manager
from service_instances import *

auth_blueprint = Blueprint('auth', __name__)

class Authorization:
    def __init__(self):
        self.status = True 

    def start(self):
        self.status = True

    def stop(self):
        self.status = False

    def check_status(self):
        return self.status

authorization = Authorization()
auth_blueprint.errorhandler(DomainError)(handle_domain_error)
auth_blueprint.errorhandler(DataStorageError)(handle_data_storage_error)
auth_blueprint.errorhandler(MapperError)(handle_mapper_error)
auth_blueprint.errorhandler(AuthenticationError)(handle_authentication_error)
auth_blueprint.errorhandler(ExtractionError)(handle_extraction_error)
auth_blueprint.errorhandler(ValidationError)(handle_validation_error)
auth_blueprint.errorhandler(AuthorizationError)(handle_authorization_error)

@check_service_status(AuthorizationError)
@auth_blueprint.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        username, password = extraction.extract_login_credentials(request.form)
        is_valid, errors = validation.validate_login_credentials(username, password)

        if is_valid:
            if authentication.authenticate_and_login(username, password, 'patient'):
                return redirect(url_for('auth.patient_dashboard'))
            else:
                flash('Invalid username or password')
        else:
            for field, error in errors.items():
                flash(f"{field}: {error}")

    return render_template('patient_login.html')

@check_service_status(AuthorizationError)
@auth_blueprint.route('/provider_login', methods=['GET', 'POST'])
def provider_login():
    if request.method == 'POST':
        username, password = extraction.extract_login_credentials(request.form)
        is_valid, errors = validation.validate_login_credentials(username, password)
        if is_valid:
            provider_record = extraction.get_provider_record_by_username(username)
            if provider_record:
                user_type = provider_record['user_type']
                if authentication.authenticate_and_login(username, password, user_type):
                    
                    if user_type == "staff":
                        return redirect(url_for('auth.staff_dashboard'))
                    elif user_type == "doctor":
                        return redirect(url_for('auth.doctor_dashboard'))
                    elif user_type == "admin":
                        return redirect(url_for('auth.admin_dashboard'))
                else:
                    flash('Invalid username or password')
        else:
            for field, error in errors.items():
                flash(f"{field}: {error}")
    
    return render_template('provider_login.html')

@check_service_status(AuthorizationError)
@auth_blueprint.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    authentication.perform_logout()
    return redirect(url_for('auth.home'))

@check_service_status(AuthorizationError)
@auth_blueprint.route('/')
def home():
    return render_template('welcome.html')

@check_service_status(AuthorizationError)
@auth_blueprint.route('/staff_dashboard')
@login_required
def staff_dashboard():
    if current_user.user_type != 'staff':
        return unauthorized_callback()
    return render_template('staff_dashboard.html', login_success=True)

@check_service_status(AuthorizationError)
@auth_blueprint.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.user_type != 'admin':
        return unauthorized_callback()
    return render_template('admin_dashboard.html', login_success=True)

@check_service_status(AuthorizationError)
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('You must be logged in to view this page.')
    return redirect(url_for('home'))

@check_service_status(AuthorizationError)
@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        reg_data = extraction.extract_registration_data(request.form)
        valid, error_message = validation.validate_password(reg_data['password'], reg_data['confirm_password'])
        if not valid:
            flash(error_message)
            return render_template('register.html')
        
        existing_user = mapper.get_user_by_username(reg_data['username'], reg_data['user_type'])
        if existing_user:
            flash('Username already taken. Please choose another.')
            return render_template('register.html')

        hashed_password = generate_password_hash(reg_data['password'])
        domain.create_user(reg_data['username'], hashed_password, reg_data['security_question'], reg_data['security_answer'], reg_data['user_type'])
        flash('Registration successful. Please log in.')
        return redirect(url_for('auth.patient_login'))

    return render_template('register.html')

@check_service_status(AuthorizationError)
@auth_blueprint.route('/change_password', methods=['GET'])
def change_password():
    return render_template('request_username.html')

@check_service_status(AuthorizationError)
@auth_blueprint.route('/verify_username', methods=['POST'])
def verify_username():
    username = extraction.extract_username(request.form)
    result = extraction.get_user_security_question(username)

    if result:
        session['user_id'] = result['id']
        question_text = validation.get_question_text_by_id(result['question_id'])
        return render_template('answer_security_question.html', question=question_text)
    else:
        flash('Username not found or no security question set for this user.')
        return redirect(url_for('auth.change_password'))

@check_service_status(AuthorizationError)
@auth_blueprint.route('/change_password_final', methods=['POST'])
def change_password_final():
    form_data = extraction.extract_change_password_data(request.form)
    answer = form_data['answer']
    new_password = form_data['new_password']
    confirm_new_password = form_data['confirm_new_password']

    if new_password != confirm_new_password:
        flash('New passwords do not match.')
        return redirect(url_for('auth.verify_username'))

    user_id = session.get('user_id')
    if not user_id:
        flash('User session expired or invalid. Please start the process again.')
        return redirect(url_for('auth.change_password'))

    if not extraction.verify_security_answer(user_id, answer):
        flash('Incorrect answer to security question.')
        return redirect(url_for('auth.verify_username'))

    hashed_password = generate_password_hash(new_password)
    extraction.update_user_password(user_id, hashed_password)

    session.pop('user_id', None)
    flash('Your password has been updated successfully.')
    return redirect(url_for('auth.patient_login'))

@check_service_status(AuthorizationError)
@auth_blueprint.route('/doctor_dashboard')
@login_required
def doctor_dashboard():  
    if current_user.user_type != 'doctor':
        return unauthorized_callback()
    from services.domain import Booking
    bookings = Booking.query.all()
    return render_template('index.html', bookings=bookings)

@check_service_status(AuthorizationError)
@auth_blueprint.route('/add_booking', methods=['POST'])
@login_required
def add_booking():
    booking_data = extraction.extract_booking_data(request.form)
    from services.domain import Booking
    new_booking = Booking(**booking_data)
    domain.add_to_db(new_booking)

    return redirect(url_for('auth.doctor_dashboard'))

@check_service_status(AuthorizationError)
@auth_blueprint.route('/delete_booking/<int:id>', methods=['POST'])
@login_required
def delete_booking(id): 
    booking = extraction.get_booking_by_id(id)
    domain.delete_from_db(booking)
    

    return redirect(url_for('auth.doctor_dashboard'))

@check_service_status(AuthorizationError)
@auth_blueprint.route('/update_booking/<int:id>', methods=['POST'])
@login_required
def update_booking(id):
    booking = extraction.get_booking_by_id(id)
    booking_data = extraction.extract_booking_data(request.form)
    for key, value in booking_data.items():
        setattr(booking, key, value)
    
    return redirect(url_for('auth.doctor_dashboard'))

@check_service_status(AuthorizationError)
@auth_blueprint.route('/patient_dashboard')
@login_required
def patient_dashboard():  
    if current_user.user_type != 'patient':
        return unauthorized_callback()
    return render_template('patient_dashboard.html', login_success=True)

@check_service_status(AuthorizationError)
@auth_blueprint.route('/book-appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():  
    if request.method == 'POST':
        user_id = session.get('user_id', 1)
        appointment = extraction.extract_appointment_data(request.form, user_id)
        domain.add_to_db(appointment)
        
        return redirect(url_for('auth.view_appointments'))
    else:
        from services.domain import Doctor
        doctors = Doctor.query.all()
        return render_template('book_appointment.html', doctors=doctors)
    
@check_service_status(AuthorizationError)
@auth_blueprint.route('/change-appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def change_appointment(appointment_id):
    appointment = extraction.get_appointment_by_id(appointment_id)
    if request.method == 'POST':
        new_datetime = extraction.extract_appointment_update_data(request.form)
        appointment.time = new_datetime
        
        return redirect(url_for('auth.view_appointments'))
    else:
        return render_template('change_appointment.html', appointment=appointment)

@check_service_status(AuthorizationError)
@auth_blueprint.route('/update-insurance', methods=['GET', 'POST'])
@login_required
def update_insurance():
    insurance_id = 1  # Placeholder for actual insurance ID retrieval logic
    insurance = extraction.get_insurance_by_id(insurance_id)

    if request.method == 'POST' and insurance:
        insurance_data = extraction.extract_insurance_update_data(request.form)
        for key, value in insurance_data.items():
            setattr(insurance, key, value)
        
        return redirect(url_for('auth.patient_dashboard'))

    return render_template('update_insurance.html', insurance=insurance)

@check_service_status(AuthorizationError)
@auth_blueprint.route('/view-appointments')
@login_required
def view_appointments():
    appointments = extraction.view_user_appointments()
    return render_template('view_appointments.html', appointments=appointments)

@check_service_status(AuthorizationError)
@auth_blueprint.route('/cancel-appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = extraction.get_appointment_by_id(appointment_id)
    domain.delete_from_db(appointment)
    return redirect(url_for('auth.view_appointments'))

@check_service_status(AuthorizationError)
@auth_blueprint.route('/modify-appointment/<int:appointment_id>', methods=['GET'])
@login_required
def modify_appointment(appointment_id):
    appointment = extraction.get_appointment_by_id(appointment_id)
    return render_template('change_appointment.html', appointment=appointment)


