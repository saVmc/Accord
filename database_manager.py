import sqlite3 as sql

DB_PATH = "database/data_source.db"

def list_users():
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    data = cur.execute("SELECT * FROM users").fetchall()
    con.close()
    return data

def get_user_by_email(email):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    con.close()
    return user

def create_user(name, email, password, role):
    con = sql.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, password, role))
    con.commit()
    con.close()
