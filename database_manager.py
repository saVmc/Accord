import sqlite3 as sql
import random
import string
from datetime import datetime

DB_PATH = "database/data_source.db"

def get_connection():
    con = sql.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def init_db():
    con = get_connection()
    cur = con.cursor()

    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        userID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('teacher','student')),
        avatar TEXT
    );
    """)

    # CLASSES
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

    # ENROLLMENTS
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

    # CLASS MESSAGES (WITH IMAGES)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS class_messages (
        messageID INTEGER PRIMARY KEY AUTOINCREMENT,
        classID INTEGER NOT NULL,
        senderID INTEGER NOT NULL,
        content TEXT,
        imageURL TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (classID) REFERENCES classes(classID),
        FOREIGN KEY (senderID) REFERENCES users(userID)
    );
    """)

    # ASSIGNMENTS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        assignmentID INTEGER PRIMARY KEY AUTOINCREMENT,
        classID INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        dueDate DATE NOT NULL,
        FOREIGN KEY (classID) REFERENCES classes(classID)
    );
    """)

    # SUBMISSIONS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        submissionID INTEGER PRIMARY KEY AUTOINCREMENT,
        assignmentID INTEGER NOT NULL,
        studentID INTEGER NOT NULL,
        fileLink TEXT NOT NULL,
        submittedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        grade TEXT,
        feedback TEXT,
        FOREIGN KEY (assignmentID) REFERENCES assignments(assignmentID),
        FOREIGN KEY (studentID) REFERENCES users(userID)
    );
    """)

    # DM THREADS (DM + GROUP DM)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dm_threads (
        threadID INTEGER PRIMARY KEY AUTOINCREMENT,
        isGroup INTEGER DEFAULT 0,
        threadName TEXT,
        createdBy INTEGER,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS dm_participants (
        threadID INTEGER,
        userID INTEGER,
        PRIMARY KEY (threadID, userID),
        FOREIGN KEY (threadID) REFERENCES dm_threads(threadID),
        FOREIGN KEY (userID) REFERENCES users(userID)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS dm_messages (
        messageID INTEGER PRIMARY KEY AUTOINCREMENT,
        threadID INTEGER NOT NULL,
        senderID INTEGER NOT NULL,
        content TEXT,
        imageURL TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (threadID) REFERENCES dm_threads(threadID),
        FOREIGN KEY (senderID) REFERENCES users(userID)
    );
    """)

    con.commit()
    con.close()

# -------- USER HELPERS --------
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

def create_user(name, email, password, role, avatar=None):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO users (name, email, password, role, avatar) VALUES (?, ?, ?, ?, ?)", (name, email, password, role, avatar))
    con.commit()
    con.close()

def update_user(userID, name=None, email=None, password=None, avatar=None):
    con = get_connection()
    cur = con.cursor()
    if name:
        cur.execute("UPDATE users SET name = ? WHERE userID = ?", (name, userID))
    if email:
        cur.execute("UPDATE users SET email = ? WHERE userID = ?", (email, userID))
    if password:
        cur.execute("UPDATE users SET password = ? WHERE userID = ?", (password, userID))
    if avatar is not None:
        cur.execute("UPDATE users SET avatar = ? WHERE userID = ?", (avatar, userID))
    con.commit()
    con.close()

def search_users_by_name_email(query):
    con = get_connection()
    cur = con.cursor()
    q = f"%{query.lower()}%"
    cur.execute("SELECT userID, name, email, avatar FROM users WHERE lower(name) LIKE ? OR lower(email) LIKE ?", (q, q))
    results = cur.fetchall()
    con.close()
    return results

# -------- CLASSES & ENROLLMENTS --------
def generate_class_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_class(className, teacherID, description=None):
    con = get_connection()
    cur = con.cursor()
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
        SELECT u.userID, u.name, u.email, u.avatar
        FROM users u
        JOIN enrollments e ON u.userID = e.studentID
        WHERE e.classID = ?
    """, (classID,))
    rows = cur.fetchall()
    con.close()
    return rows

# -------- CLASS MESSAGES --------
def add_class_message(classID, senderID, content, imageURL=None):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO class_messages (classID, senderID, content, imageURL) VALUES (?, ?, ?, ?)",
                (classID, senderID, content, imageURL))
    con.commit()
    con.close()

def list_class_messages(classID, limit=100):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT cm.messageID, cm.classID, cm.senderID, cm.content, cm.timestamp, u.name, u.avatar, cm.imageURL
        FROM class_messages cm
        JOIN users u ON cm.senderID = u.userID
        WHERE cm.classID = ?
        ORDER BY cm.timestamp DESC
        LIMIT ?
    """, (classID, limit))
    rows = cur.fetchall()
    con.close()
    return rows

# --------- ASSIGNMENTS ---------
def create_assignment(classID, title, description, dueDate):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO assignments (classID, title, description, dueDate) VALUES (?, ?, ?, ?)",
        (classID, title, description, dueDate)
    )
    con.commit()
    con.close()

def get_assignments_for_class(classID):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM assignments WHERE classID = ? ORDER BY dueDate ASC",
        (classID,)
    )
    rows = cur.fetchall()
    con.close()
    return rows

def get_assignment_by_id(assignmentID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM assignments WHERE assignmentID = ?", (assignmentID,))
    row = cur.fetchone()
    con.close()
    return row

def submit_assignment(assignmentID, studentID, fileLink):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO submissions (assignmentID, studentID, fileLink) VALUES (?, ?, ?)",
        (assignmentID, studentID, fileLink)
    )
    con.commit()
    con.close()

def get_submissions_for_assignment(assignmentID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT s.*, u.name, u.avatar
        FROM submissions s
        JOIN users u ON s.studentID = u.userID
        WHERE s.assignmentID = ?
        ORDER BY s.submittedAt DESC
    """, (assignmentID,))
    rows = cur.fetchall()
    con.close()
    return rows

def get_submission_by_student(assignmentID, studentID):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM submissions WHERE assignmentID = ? AND studentID = ?",
        (assignmentID, studentID)
    )
    row = cur.fetchone()
    con.close()
    return row

def grade_submission(submissionID, grade, feedback):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "UPDATE submissions SET grade = ?, feedback = ? WHERE submissionID = ?",
        (grade, feedback, submissionID)
    )
    con.commit()
    con.close()

# --------- DMs & GROUP CHATS ---------
def create_dm_thread(participant_ids, isGroup=False, threadName=None, createdBy=None):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO dm_threads (isGroup, threadName, createdBy) VALUES (?, ?, ?)",
        (1 if isGroup else 0, threadName, createdBy)
    )
    threadID = cur.lastrowid
    for uid in set(participant_ids):
        cur.execute("INSERT INTO dm_participants (threadID, userID) VALUES (?, ?)", (threadID, uid))
    con.commit()
    con.close()
    return threadID

def get_threads_for_user(userID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT t.threadID, t.isGroup, t.threadName, t.createdAt
        FROM dm_threads t
        JOIN dm_participants p ON t.threadID = p.threadID
        WHERE p.userID = ?
        ORDER BY t.createdAt DESC
    """, (userID,))
    rows = cur.fetchall()
    con.close()
    return rows

def get_thread_participants(threadID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT u.userID, u.name, u.email, u.avatar
        FROM dm_participants p
        JOIN users u ON p.userID = u.userID
        WHERE p.threadID = ?
    """, (threadID,))
    results = cur.fetchall()
    con.close()
    return results

def add_dm_message(threadID, senderID, content, imageURL=None):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO dm_messages (threadID, senderID, content, imageURL) VALUES (?, ?, ?, ?)",
        (threadID, senderID, content, imageURL)
    )
    con.commit()
    con.close()

def list_dm_messages(threadID, limit=200):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT m.messageID, m.threadID, m.senderID, m.content, m.imageURL, m.timestamp, u.name, u.avatar
        FROM dm_messages m
        JOIN users u ON m.senderID = u.userID
        WHERE m.threadID = ?
        ORDER BY m.timestamp ASC
        LIMIT ?
    """, (threadID, limit))
    rows = cur.fetchall()
    con.close()
    return rows

def user_in_thread(userID, threadID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT 1 FROM dm_participants WHERE userID = ? AND threadID = ?", (userID, threadID))
    result = cur.fetchone()
    con.close()
    return bool(result)

# --------- CLASS/USER DELETE ---------
def delete_class(classID, teacherID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM classes WHERE classID = ? AND teacherID = ?", (classID, teacherID))
    cur.execute("DELETE FROM enrollments WHERE classID = ?", (classID,))
    cur.execute("DELETE FROM class_messages WHERE classID = ?", (classID,))
    cur.execute("DELETE FROM assignments WHERE classID = ?", (classID,))
    con.commit()
    con.close()

def unenroll_student(classID, studentID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM enrollments WHERE classID = ? AND studentID = ?", (classID, studentID))
    con.commit()
    con.close()

def get_dm_thread_between_users(user1_id, user2_id):
    """
    Checks if a one-on-one DM thread exists between user1 and user2.
    Returns the thread ID if it exists, otherwise None.
    """
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT t.threadID
        FROM dm_threads t
        JOIN dm_participants p1 ON t.threadID = p1.threadID
        JOIN dm_participants p2 ON t.threadID = p2.threadID
        WHERE t.isGroup = 0 AND p1.userID = ? AND p2.userID = ?
    """, (user1_id, user2_id))
    row = cur.fetchone()
    con.close()
    if row:
        return row[0] # threadID
    return None

def get_thread_name(threadID):
    """
    Returns the threadName for a DM or group chat.
    """
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT threadName FROM dm_threads WHERE threadID = ?", (threadID,))
    row = cur.fetchone()
    con.close()
    return row[0] if row else None

def rename_thread(threadID, new_name):
    """
    Updates the threadName for a given thread.
    """
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE dm_threads SET threadName = ? WHERE threadID = ?", (new_name, threadID))
    con.commit()
    con.close()
