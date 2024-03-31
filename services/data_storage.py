from extensions import db
from services.exceptions import DataStorageError, check_service_status

class DataStorage:
    def __init__(self):
        self.status = True
        self.connection = None

    def start(self):
        self.status = True

    def stop(self):
        self.status = False
        if self.connection and self.connection.is_connected():

            self.connection.close()
            print("Closed the database connection.")
            self.connection = None

    def check_status(self):
        return self.status

    @check_service_status(DataStorageError)
    def get_db_connection(self):
        if self.connection and self.connection.is_connected():
            return self.connection

        try:
            import mysql.connector
            db_config = {
                'host': 'localhost',
                'user': 'root',
                'password': 'password',
                'database': 'layered_architecture'
            }
            self.connection = mysql.connector.connect(**db_config)
            return self.connection
        except Exception as e:
            raise DataStorageError from e