from flask import Flask, render_template, request, redirect, url_for, session, flash
import database_manager as db


## MEGA BIG MAIN.PY, with some comments to help me remember what each part does :]



app = Flask(__name__)
app.secret_key = "supersecretkey" # CHANGE THIS LATERR (i will forget)

# double check all the tables exist s no errors
db.init_db()

def logged_in_user():
    return session.get("user")  # return with user id, name, email, role

# Routes list - will be expanded in future :)

@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def index():
    user = logged_in_user()
    return render_template("index.html", user=user)

# ---------- AUTH ---------- (specifically for login/signup/logout)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = db.get_user_by_email(email)
        if user and user[3] == password:
            # user tuple: (userID, name, email, password, role)
            session["user"] = {"id": user[0], "name": user[1], "email": user[2], "role": user[4]}
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password", "danger")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "").strip()

        if not (name and email and password and role):
            flash("Please fill all fields", "warning")
            return redirect(url_for("signup"))

        existing_user = db.get_user_by_email(email)
        if existing_user:
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("login"))

        db.create_user(name, email, password, role)
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out", "info")
    return redirect(url_for("index"))

# Classes - functionality for the basic classes 
@app.route("/classes")
def classes():
    user = logged_in_user()
    if not user:
        flash("Please log in.")
        return redirect(url_for("login"))

    classes = db.list_classes_for_user(user["id"], user["role"])
    return render_template("classes.html", classes=classes, user=user)

@app.route("/create_class", methods=["GET", "POST"])
def create_class():
    user = logged_in_user()
    if not user or user["role"] != "teacher":
        flash("Only teachers can create classes.")
        return redirect(url_for("classes"))

    if request.method == "POST":
        class_name = request.form.get("class_name", "").strip()
        if not class_name:
            flash("Enter a class name.", "warning")
            return redirect(url_for("create_class"))
        code = db.create_class(class_name, user["id"])
        flash(f"Class '{class_name}' created — code: {code}", "success")
        return redirect(url_for("classes"))

    return render_template("create_class.html", user=user)

@app.route("/join_class", methods=["GET", "POST"])
def join_class():
    user = logged_in_user()
    if not user or user["role"] != "student":
        flash("Only students can join classes.")
        return redirect(url_for("classes"))

    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        if not code:
            flash("Enter a class code.", "warning")
            return redirect(url_for("join_class"))
        c = db.get_class_by_code(code)
        if c:
            db.enroll_student(c[0], user["id"])  # c[0] is classID
            flash(f"Joined class '{c[1]}'", "success")
            return redirect(url_for("classes"))
        else:
            flash("Invalid class code.", "danger")

    return render_template("join_class.html", user=user)

@app.route("/class/<int:class_id>")
def class_detail(class_id):
    user = logged_in_user()
    if not user:
        flash("Please log in.")
        return redirect(url_for("login"))

    c = db.get_class_by_id(class_id)
    if not c:
        flash("Class not found.", "danger")
        return redirect(url_for("classes"))

    teacher = db.get_user_by_id(c[3])  # c tuple once again: (classID, className, code, teacherID)
    students = db.list_students_in_class(class_id)
    return render_template("class_detail.html", class_row=c, teacher=teacher, students=students, user=user)

# ------------------------
# RUNNING THE WEBPAGE
# -------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
