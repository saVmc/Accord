import sqlite3 as sql
import random, string

#### N.B, i've been noting what each of my functions do, because I probably will forget :>

DB_PATH = "database/data_source.db"

def init_db():
    con = sql.connect(DB_PATH)
    cur = con.cursor()

    ## Creating the tables if they don't exist, just in case 
    
    # Create users table
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        userID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('teacher','student'))
    )''')

    # Create classes table 
    cur.execute('''CREATE TABLE IF NOT EXISTS classes (
        classID INTEGER PRIMARY KEY AUTOINCREMENT,
        className TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        teacherID INTEGER,
        FOREIGN KEY (teacherID) REFERENCES users(userID)
    )''')

    # Create enrollments table
    cur.execute('''CREATE TABLE IF NOT EXISTS enrollments (
        enrollmentID INTEGER PRIMARY KEY AUTOINCREMENT,
        classID INTEGER,
        studentID INTEGER,
        FOREIGN KEY (classID) REFERENCES classes(classID),
        FOREIGN KEY (studentID) REFERENCES users(userID)
    )''')

    con.commit()
    con.close()

# Function to make random class code
def generate_class_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6 )) ##6 digit code

# Making the class (for the teacher users)
def create_class(className, teacherID):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    code = generate_class_code()
    cur.execute("INSERT INTO classes (className, code, teacherID) VALUES (?, ?, ?)",
                (className, code, teacherID))
    con.commit()
    con.close()
    return code

# Using the code to lookup the class data
def get_class_by_code(code):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM classes WHERE code = ?", (code,))
    c = cur.fetchone()
    con.close()
    return c

# Connecting the class and student through SQL + the code given
def enroll_student(classID, studentID):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO enrollments (classID, studentID) VALUES (?, ?)",
                (classID, studentID))
    con.commit()
    con.close()

# Getting the classes, changed based on if teacher or student
def list_classes_for_user(userID, role):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    if role == "teacher":
        cur.execute("SELECT * FROM classes WHERE teacherID = ?", (userID,))
    else:  # student
        cur.execute("""SELECT c.* FROM classes c
                       JOIN enrollments e ON c.classID = e.classID
                       WHERE e.studentID = ?""", (userID,))
    classes = cur.fetchall()
    con.close()
    return classes

# Looking up the user by their emails
def get_user_by_email(email):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    con.close()
    return user

# Creating an account + adding them to the user table
def create_user(name, email, password, role):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, password, role))
    con.commit()
    con.close()
