from flask import Flask
from extensions import db
from services.domain import User
from services.authorization import *
from service_instances import authentication, extraction, domain
from services.status import status_blueprint
from services.exceptions import errors_blueprint

app = Flask(__name__)
app.secret_key = 'secret_key'
app.register_blueprint(auth_blueprint)
app.register_blueprint(status_blueprint)
app.register_blueprint(errors_blueprint)

password = "password"
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password}@localhost/layered_architecture'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from phase3_services.handle_api_request import init_appointment_routes
from phase3_services.send_api_request import init_send_request_route
from phase3_services.store_api_data import store_data

init_appointment_routes(app)
init_send_request_route(app)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

if __name__ == '__main__':
    app.run(debug=True)

authentication.set_app(app)

with app.app_context():
    db.create_all()
    domain.insert_doctor_data()

@login_manager.user_loader
def load_user(user_id):
    check_login_services()
    return User.query.get(int(user_id))

def login_services_operational():
    return (
        authentication.check_status() and
        datastorage.check_status() and
        extraction.check_status() and
        authorization.check_status()  
    )

@app.before_request
def check_login_services():
    exempt_endpoints = [
        'auth.home', 'auth.patient_login', 'auth.provider_login', 'auth.logout', 'auth.register', 'auth.change_password', 
        'auth.verify_username', 'auth.change_password_final', 'static',
        'status.change_auth_status', 'status.change_mapper_status', 'status.change_extraction_status',
        'status.change_datastorage_status', 'status.change_validation_status', 'status.change_domain_status',
        'status.change_authorization_status'
    ]

    if request.endpoint not in exempt_endpoints:
        down_services = []
        if not authentication.check_status():
            down_services.append('Authentication Service')
        if not datastorage.check_status():
            down_services.append('Data Storage Service')
        if not extraction.check_status():
            down_services.append('Extraction Service')
        if not authorization.check_status():
            down_services.append('Authorization Service')

        if down_services:
            services_string = ", ".join(down_services)
            flash(f"The following services are currently unavailable: {services_string}. Failed to authenticate user.")
            return redirect(url_for('auth.home'))
