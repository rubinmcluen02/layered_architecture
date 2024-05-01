import unittest
from app import app, db, Booking

class TestBookingApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        if not hasattr(app, 'is_db_initialized'):
            db.init_app(app)
            app.is_db_initialized = True 
        with app.app_context():
            db.create_all()


    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_booking(self):
        with app.test_client() as client:
            response = client.post('/add_booking', data=dict(
                patient_name='John Doe',
                doctor_name='Dr. Smith',
                date='2024-03-05',
                time='10:00 AM'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'John Doe', response.data)
            self.assertIn(b'Dr. Smith', response.data)

    def test_delete_booking(self):
        booking = Booking(patient_name='Jane Doe', doctor_name='Dr. Johnson', date='2024-03-06', time='11:00 AM')
        with app.app_context():
            db.session.add(booking)
            db.session.commit()
            booking_id = booking.id

        with app.test_client() as client:
            response = client.post(f'/delete_booking/{booking_id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b'Jane Doe', response.data)
            self.assertNotIn(b'Dr. Johnson', response.data)

    def test_update_booking(self):
        booking = Booking(patient_name='Jane Doe', doctor_name='Dr. Johnson', date='2024-03-06', time='11:00 AM')
        with app.app_context():
            db.session.add(booking)
            db.session.commit()
            booking_id = booking.id

        with app.test_client() as client:
            response = client.post(f'/update_booking/{booking_id}', data=dict(
                patient_name='Updated Name',
                doctor_name='Updated Doctor',
                date='2024-03-07',
                time='1:00 PM'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Updated Name', response.data)
            self.assertIn(b'Updated Doctor', response.data)
            self.assertNotIn(b'Jane Doe', response.data)
            self.assertNotIn(b'Dr. Johnson', response.data)

if __name__ == '__main__':
    unittest.main()