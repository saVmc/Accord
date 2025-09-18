import sqlite3 as sql
import random
import string
from datetime import datetime

DB_PATH = "database/data_source.db"

def get_connection():
    con = sql.connect(DB_PATH)
    # Enable foreign keys
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def init_db():
    con = get_connection()
    cur = con.cursor()

    # users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        userID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('teacher','student'))
    );
    """)

    # classes table (include description column here)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        classID INTEGER PRIMARY KEY AUTOINCREMENT,
        className TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        teacherID INTEGER NOT NULL,
        description TEXT,
        FOREIGN KEY (teacherID) REFERENCES users(userID)
    );
    """)

    # enrollments table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        enrollmentID INTEGER PRIMARY KEY AUTOINCREMENT,
        classID INTEGER NOT NULL,
        studentID INTEGER NOT NULL,
        UNIQUE(classID, studentID),
        FOREIGN KEY (classID) REFERENCES classes(classID),
        FOREIGN KEY (studentID) REFERENCES users(userID)
    );
    """)

    # class_messages table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS class_messages (
        messageID INTEGER PRIMARY KEY AUTOINCREMENT,
        classID INTEGER NOT NULL,
        senderID INTEGER NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (classID) REFERENCES classes(classID),
        FOREIGN KEY (senderID) REFERENCES users(userID)
    );
    """)

    con.commit()
    con.close()

# -----------------------------
# User helpers
# -----------------------------
def get_user_by_email(email):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    u = cur.fetchone()
    con.close()
    return u

def get_user_by_id(userID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE userID = ?", (userID,))
    u = cur.fetchone()
    con.close()
    return u

def create_user(name, email, password, role):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, password, role))
    con.commit()
    con.close()

def update_user(userID, name=None, email=None, password=None):
    # only update the provided fields
    con = get_connection()
    cur = con.cursor()
    if name:
        cur.execute("UPDATE users SET name = ? WHERE userID = ?", (name, userID))
    if email:
        cur.execute("UPDATE users SET email = ? WHERE userID = ?", (email, userID))
    if password:
        cur.execute("UPDATE users SET password = ? WHERE userID = ?", (password, userID))
    con.commit()
    con.close()

# -----------------------------
# Classes & enrollments
# -----------------------------
def generate_class_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_class(className, teacherID, description=None):
    con = get_connection()
    cur = con.cursor()
    # try to generate a unique code
    for _ in range(10):
        code = generate_class_code()
        try:
            cur.execute("INSERT INTO classes (className, code, teacherID, description) VALUES (?, ?, ?, ?)",
                        (className, code, teacherID, description))
            con.commit()
            con.close()
            return code
        except sql.IntegrityError:
            continue
    con.close()
    raise Exception("Could not generate unique class code — try again.")

def get_class_by_code(code):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM classes WHERE code = ?", (code,))
    c = cur.fetchone()
    con.close()
    return c

def get_class_by_id(classID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM classes WHERE classID = ?", (classID,))
    c = cur.fetchone()
    con.close()
    return c

def update_class(classID, className=None, description=None):
    con = get_connection()
    cur = con.cursor()
    if className is not None:
        cur.execute("UPDATE classes SET className = ? WHERE classID = ?", (className, classID))
    if description is not None:
        cur.execute("UPDATE classes SET description = ? WHERE classID = ?", (description, classID))
    con.commit()
    con.close()

def enroll_student(classID, studentID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO enrollments (classID, studentID) VALUES (?, ?)", (classID, studentID))
    con.commit()
    con.close()

def is_student_enrolled(classID, studentID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT 1 FROM enrollments WHERE classID = ? AND studentID = ?", (classID, studentID))
    r = cur.fetchone()
    con.close()
    return bool(r)

def list_classes_for_user(userID, role):
    con = get_connection()
    cur = con.cursor()
    if role == "teacher":
        cur.execute("SELECT * FROM classes WHERE teacherID = ?", (userID,))
    else:
        cur.execute("""
            SELECT c.* FROM classes c
            JOIN enrollments e ON c.classID = e.classID
            WHERE e.studentID = ?
        """, (userID,))
    classes = cur.fetchall()
    con.close()
    return classes

def list_students_in_class(classID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT u.userID, u.name, u.email
        FROM users u
        JOIN enrollments e ON u.userID = e.studentID
        WHERE e.classID = ?
    """, (classID,))
    rows = cur.fetchall()
    con.close()
    return rows

# -----------------------------
# Class messages
# -----------------------------
def add_class_message(classID, senderID, content):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO class_messages (classID, senderID, content) VALUES (?, ?, ?)",
                (classID, senderID, content))
    con.commit()
    con.close()

def list_class_messages(classID, limit=100):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT cm.messageID, cm.classID, cm.senderID, cm.content, cm.timestamp, u.name
        FROM class_messages cm
        JOIN users u ON cm.senderID = u.userID
        WHERE cm.classID = ?
        ORDER BY cm.timestamp DESC
        LIMIT ?
    """, (classID, limit))
    rows = cur.fetchall()
    con.close()
    return rows

# -----------------------------
# Class delete / unenroll
# -----------------------------
def delete_class(classID, teacherID):
    con = get_connection()
    cur = con.cursor()
    # Only delete if teacher owns this class
    cur.execute("DELETE FROM classes WHERE classID = ? AND teacherID = ?", (classID, teacherID))
    # cleanup enrollments & messages
    cur.execute("DELETE FROM enrollments WHERE classID = ?", (classID,))
    cur.execute("DELETE FROM class_messages WHERE classID = ?", (classID,))
    con.commit()
    con.close()

def unenroll_student(classID, studentID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM enrollments WHERE classID = ? AND studentID = ?", (classID, studentID))
    con.commit()
    con.close()
    