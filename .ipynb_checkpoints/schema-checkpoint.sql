-- Create the User table
CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- Create the Insurance table
CREATE TABLE IF NOT EXISTS Insurance (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    policy_number VARCHAR(100) NOT NULL,
    dob VARCHAR(100) NOT NULL,
    address VARCHAR(200),
    phone VARCHAR(100),
    copay FLOAT,
    deductible FLOAT,
    coinsurance FLOAT,
    out_of_pocket_max FLOAT,
    covered_services TEXT
);

-- Create the Doctor table
CREATE TABLE IF NOT EXISTS Doctor (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(200) NOT NULL,
    specialization VARCHAR(100) NOT NULL
);

-- Create the Appointment table
CREATE TABLE IF NOT EXISTS Appointment (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    time DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(id)
);
