import sqlite3 as sql
import random, string

DB_PATH = "database/data_source.db"

# Utility: connect to DB
def get_connection():
    return sql.connect(DB_PATH)

# -------------------------------
# User Management
# -------------------------------
def get_user_by_email(email):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    con.close()
    return user

def create_user(name, email, password, role):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, password, role))
    con.commit()
    con.close()

# -------------------------------
# Class Management
# -------------------------------
def generate_class_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_class(className, teacherID):
    con = get_connection()
    cur = con.cursor()
    code = generate_class_code()
    cur.execute("INSERT INTO classes (className, code, teacherID) VALUES (?, ?, ?)",
                (className, code, teacherID))
    con.commit()
    con.close()
    return code  # return join code for students

def get_class_by_code(code):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM classes WHERE code = ?", (code,))
    c = cur.fetchone()
    con.close()
    return c

def enroll_student(classID, studentID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO enrollments (classID, studentID) VALUES (?, ?)",
                (classID, studentID))
    con.commit()
    con.close()

def list_classes_for_user(userID, role):
    con = get_connection()
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
