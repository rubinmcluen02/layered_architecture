How to run web app:
1. Start MySQL server on localhost
2. Change password in app.py to your personal password for MySQL
3. In the terminal, run "python create_db.py"
4. In the terminal, run "flask run"
5. In your browser, search "http://127.0.0.1:5000"

How to log in:
As a Patient:
    1. Click Patient Login
    2. Type in username: "test", password: "Pass1"
    3. Click Login
    You can also register a new account.
    
As a Doctor:
    1. Click Provider Login
    2. Type in username: "doctor", password: "Pass1"
    3. Click Login
    
Note: Passwords must be at least 5 characters, have a capital letter, and have a number.

How to run tests:

1. Make sure web app is running
2. In the terminal, run "python test.py"

Note: You may need to download Selenium/Chrome Driver to run tests