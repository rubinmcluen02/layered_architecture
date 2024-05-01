import unittest
from app import app, db, User, Insurance, Doctor, Appointment
from datetime import datetime

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()

        self.app_context = app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Patient Portal', response.data)

    def test_login_route(self):
        response = self.app.post('/login', data=dict(username='test_user', password='test_password'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Explore the available options', response.data)

    def test_book_appointment_route(self):
        doctor = Doctor(name='Dr. Test', address='123 Test St', specialization='Test Specialty')
        db.session.add(doctor)
        db.session.commit()

        response = self.app.post('/book-appointment', data=dict(doctor_id=1, appointment_date='2024-03-01', appointment_time='08:00'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your Appointments', response.data)

    def test_change_appointment_route(self):
        response = self.app.post('/login', data=dict(username='test_user', password='test_password'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        appointment = Appointment.query.first()
        if appointment:
            response = self.app.post(f'/change-appointment/{appointment.id}', data=dict(date='2024-03-02', time='14:00'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Appointment Modified', response.data)

    def test_cancel_appointment_route(self):
        response = self.app.post('/login', data=dict(username='test_user', password='test_password'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        appointment = Appointment.query.first()
        if appointment:
            response = self.app.post(f'/cancel-appointment/{appointment.id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Appointment Cancelled', response.data)
    def test_update_insurance_route(self):
        test_insurance = Insurance(name='Test Insurance', policy_number='123456', dob='1990-01-01',
                                    address='Test Address', phone='1234567890', copay=20.0, deductible=500.0,
                                    coinsurance=0.2, out_of_pocket_max=1000.0, covered_services='Test services')
        db.session.add(test_insurance)
        db.session.commit()

        response = self.app.post('/update-insurance', data=dict(name='Updated Insurance', policy_number='654321',
                                                                address='Updated Address', phone='9876543210',
                                                                copay=25.0, deductible=1000.0, coinsurance=0.1,
                                                                out_of_pocket_max=1500.0, covered_services='Updated services'),
                                 follow_redirects=True)

        self.assertEqual(response.status_code, 200) 

if __name__ == '__main__':
    unittest.main()
