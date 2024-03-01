import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash

def get_db_connection():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'layered_architecture'
    }
    return mysql.connector.connect(**db_config)

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as e:
        print(f"Error: '{e}'")

def create_table(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Table created successfully")
    except Error as e:
        print(f"Error: '{e}'")

def insert_user(username, password, user_type, security_question, security_answer):
    hashed_password = generate_password_hash(password)

    insert_user_query = """
    INSERT INTO users (username, password, user_type)
    VALUES (%s, %s, %s)
    """

    insert_security_question_query = """
    INSERT INTO security_questions (id, question_id, answer)
    VALUES (LAST_INSERT_ID(), %s, %s)
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(insert_user_query, (username, hashed_password, user_type))
        cursor.execute(insert_security_question_query, (security_question, security_answer))
        conn.commit()
        print(f"User '{username}' created successfully.")

    except Error as e:
        print(f"Error: '{e}'")
        conn.rollback()

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection is closed")

users = [
    ("test", "Pass1", "patient", 1, "Fluffy"),
    ("user1", "Pass1", "patient", 1, "Fluffy"),
    ("staff", "Pass1", "staff", 1, "NULL"),
    ("doctor", "Pass1", "doctor", 1, "NULL"),
    ("admin", "Pass1", "admin", 1, "NULL")
]

host_name = "localhost"
user_name = "root"
user_password = "password"

try:
    connection = mysql.connector.connect(
        host=host_name,
        user=user_name,
        passwd=user_password
    )

    if connection.is_connected():
        print("MySQL connection is successful")

        create_database_query = "CREATE DATABASE IF NOT EXISTS layered_architecture"
        create_database(connection, create_database_query)

        connection.database = 'layered_architecture'
        
        create_users_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            user_type VARCHAR(50) NOT NULL,
            CHECK (user_type IN ('patient', 'staff', 'doctor', 'admin'))
        )
        """
        create_table(connection, create_users_table_query)
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS security_questions (
            id INT PRIMARY KEY,
            question_id INT NOT NULL,
            answer VARCHAR(255) NOT NULL,
            FOREIGN KEY (id) REFERENCES users(id)
        )
        """
        create_table(connection, create_table_query)
        
        

except Error as e:
    print(f"Error: '{e}'")
finally:
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")
        
for user in users:
    insert_user(*user)
