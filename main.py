from flask import Flask, render_template, request, redirect, url_for, session, flash
import database_manager as db


## MEGA BIG MAIN.PY, with some comments to help me remember what each part does :]

app = Flask(__name__)
app.secret_key = "supersecretkey"  # CHANGE THIS LATERR (ill forget lol)

# double check all the tables exist so no errors (init everything in DB)
db.init_db()

def logged_in_user():
    return session.get("user")  # return current user data from table: id, name, email, role

# -------------------------
# BASIC / BORING SITE ROUTES :/
# -------------------------
@app.route("/")
@app.route("/index.html")
def index():
    user = logged_in_user()
    return render_template("index.html", user=user)

# ---------- AUTH ---------- (specifically for login/signup/logout)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user_row = db.get_user_by_email(email)
        if user_row and user_row[3] == password:
            # user info again: (userID, name, email, password, role)
            session["user"] = {"id": user_row[0], "name": user_row[1], "email": user_row[2], "role": user_row[4]}
            flash("Login successful", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "").strip()
        if not (name and email and password and role):
            flash("Please complete all fields", "warning")
            return redirect(url_for("signup"))
        existing = db.get_user_by_email(email)
        if existing:
            flash("Email already registered", "warning")
            return redirect(url_for("login"))
        db.create_user(name, email, password, role)
        flash("Account created — please log in", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out", "info")
    return redirect(url_for("index"))

# -------------------------
# USER SETTINGS (editing profile through table connection)
# -------------------------
@app.route("/settings", methods=["GET", "POST"])
def settings():
    user = logged_in_user()
    if not user:
        flash("Please log in", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        # update name/email/password through settings form
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            db.update_user(user["id"], name=name or None, email=email or None, password=password or None)
            # refresh session with fresh info
            updated = db.get_user_by_id(user["id"])
            session["user"]["name"] = updated[1]
            session["user"]["email"] = updated[2]
            flash("Settings updated", "success")
        except Exception as e:
            flash("Error updating settings: " + str(e), "danger")
        return redirect(url_for("settings"))

    # GET - put in the current user info
    current = db.get_user_by_id(user["id"])
    return render_template("settings.html", user=current)

# -------------------------
# CLASSES (all routes related to classes + that functionality)
# -------------------------
@app.route("/classes")
def classes():
    user = logged_in_user()
    if not user:
        flash("Please log in")
        return redirect(url_for("login"))
    classes = db.list_classes_for_user(user["id"], user["role"])
    return render_template("classes.html", classes=classes, user=user)

@app.route("/create_class", methods=["GET", "POST"])
def create_class():
    user = logged_in_user()
    if not user or user["role"] != "teacher":
        flash("Only teachers can create classes", "danger")
        return redirect(url_for("classes"))
    if request.method == "POST":
        class_name = request.form.get("class_name", "").strip()
        description = request.form.get("description", "").strip()
        if not class_name:
            flash("Enter class name", "warning")
            return redirect(url_for("create_class"))
        code = db.create_class(class_name, user["id"], description=description)
        flash(f"Class created: {class_name} (code: {code})", "success")
        return redirect(url_for("classes"))
    return render_template("create_class.html", user=user)

@app.route("/join_class", methods=["GET", "POST"])
def join_class():
    user = logged_in_user()
    if not user or user["role"] != "student":
        flash("Only students can join classes", "danger")
        return redirect(url_for("classes"))
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        if not code:
            flash("Enter code", "warning")
            return redirect(url_for("join_class"))
        c = db.get_class_by_code(code)
        if not c:
            flash("Invalid code", "danger")
        else:
            db.enroll_student(c[0], user["id"])  # c[0] = classID
            flash(f"Joined class '{c[1]}'", "success")
            return redirect(url_for("classes"))
    return render_template("join_class.html", user=user)

# CLASS DETAILS - shows teacher, students, description, messages etc 
@app.route("/class/<int:class_id>")
def class_detail(class_id):
    user = logged_in_user()
    if not user:
        flash("Please log in", "warning")
        return redirect(url_for("login"))

    c = db.get_class_by_id(class_id)
    if not c:
        flash("Class not found", "danger")
        return redirect(url_for("classes"))

    teacher = db.get_user_by_id(c[3])  # class tuple: (classID, className, code, teacherID, description)
    students = db.list_students_in_class(class_id)
    messages = db.list_class_messages(class_id, limit=200)
    # is the logged-in user is allowed to see/post in the class?
    enrolled = (user["role"] == "teacher" and user["id"] == c[3]) or db.is_student_enrolled(class_id, user["id"])
    return render_template("class_detail.html",
                           class_row=c, teacher=teacher, students=students,
                           messages=messages, user=user, enrolled=enrolled)

# EDIT CLASS - make sure only the teacher who created it can update name/desc
@app.route("/class/<int:class_id>/edit", methods=["POST"])
def class_edit(class_id):
    user = logged_in_user()
    if not user:
        flash("Please log in", "warning")
        return redirect(url_for("login"))

    c = db.get_class_by_id(class_id)
    if not c:
        flash("Class not found", "danger")
        return redirect(url_for("classes"))

    if user["role"] != "teacher" or user["id"] != c[3]:
        flash("Only the class teacher can edit", "danger")
        return redirect(url_for("class_detail", class_id=class_id))

    class_name = request.form.get("class_name", "").strip()
    description = request.form.get("description", "").strip()

    db.update_class(class_id, className=class_name or None, description=description or None)
    flash("Class updated", "success")
    return redirect(url_for("class_detail", class_id=class_id))

# POST MESSAGE - teacher or enrolled students can post in a class
@app.route("/class/<int:class_id>/message", methods=["POST"])
def class_message(class_id):
    user = logged_in_user()
    if not user:
        flash("Please log in", "warning")
        return redirect(url_for("login"))

    c = db.get_class_by_id(class_id)
    if not c:
        flash("Class not found", "danger")
        return redirect(url_for("classes"))

    allowed = (user["role"] == "teacher" and user["id"] == c[3]) or db.is_student_enrolled(class_id, user["id"])
    if not allowed:
        flash("You must be the teacher or enrolled to post a message", "danger")
        return redirect(url_for("class_detail", class_id=class_id))

    content = request.form.get("content", "").strip()
    if not content:
        flash("Enter a message", "warning")
        return redirect(url_for("class_detail", class_id=class_id))

    db.add_class_message(class_id, user["id"], content)
    flash("Message posted", "success")
    return redirect(url_for("class_detail", class_id=class_id))

# DELETE CLASS - teachers only, removes whole class (currently broken :<)
@app.route("/class/<int:class_id>/delete", methods=["POST"])
def delete_class_route(class_id):
    user = session.get("user")
    if not user or user["role"] != "teacher":
        flash("Not authorized", "danger")
        return redirect(url_for("classes"))
    db.delete_class(class_id, user["userID"])
    flash("Class deleted", "success")
    return redirect(url_for("classes"))

# UNENROLL - students leave a class (currently not working T^T)
@app.route("/class/<int:class_id>/unenroll", methods=["POST"])
def unenroll_class(class_id):
    user = session.get("user")
    if not user or user["role"] != "student":
        flash("Not authorized", "danger")
        return redirect(url_for("classes"))
    db.unenroll_student(class_id, user["userID"])
    flash("You left the class", "info")
    return redirect(url_for("classes"))

# ALT VERSION OF EDIT CLASS - teacher edits via GET/POST
@app.route("/class/<int:class_id>/edit", methods=["GET", "POST"])
def edit_class(class_id):
    user = session.get("user")
    if not user or user["role"] != "teacher":
        flash("Not authorized", "danger")
        return redirect(url_for("classes"))

    c = db.get_class_by_id(class_id)
    if not c or c[3] != user["userID"]:  # check if owner? (teacherID)
        flash("You don’t own this class", "danger")
        return redirect(url_for("classes"))

    if request.method == "POST":
        className = request.form.get("className") or None
        description = request.form.get("description") or None
        db.update_class(class_id, className, description)
        flash("Class updated", "success")
        return redirect(url_for("class_detail", class_id=class_id))

    return render_template("edit_class.html", class_data=c)


# ------------------------
# RUNNING THE WEBPAGE
# ------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
