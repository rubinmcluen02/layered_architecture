from services.data_storage import DataStorage
from services.exceptions import DataStorageError

def store_data(data):
    data_storage = DataStorage()
    try:
        conn = data_storage.get_db_connection()
        cursor = conn.cursor()

        booking_info = data['data'] 

        query = """
        INSERT INTO booking (id, patient_name, doctor_name, date, time)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            booking_info['id'],
            booking_info['patient_name'],
            booking_info['doctor_name'],
            booking_info['date'],
            booking_info['time']
        )
        cursor.execute(query, values)
        conn.commit()

    except DataStorageError as e:
        print(f"Error storing data: {e}")

    except KeyError as e:
        print(f"Missing key in data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()
