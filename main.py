from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import database_manager as db
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# --- CONFIG ---
app = Flask(__name__)
app.secret_key = "supersecretkey"  # CHANGE THIS TO SOMETHING SECRET

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'zip'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def logged_in_user():
    return session.get("user")

def user_avatar(user):
    return user.get('avatar') or url_for('static', filename='images/default_avatar.png')

# --- ROUTES ---

@app.route("/")
@app.route("/index.html")
def index():
    user = logged_in_user()
    return render_template("index.html", user=user)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user_row = db.get_user_by_email(email)
        if user_row and user_row[3] == password:
            session["user"] = {
                "id": user_row[0], "name": user_row[1], "email": user_row[2],
                "role": user_row[4], "avatar": user_row[5]
            }
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
        avatar_file = request.files.get("avatar")
        avatar_url = None
        if avatar_file and allowed_file(avatar_file.filename):
            filename = secure_filename(f"{email}_{avatar_file.filename}")
            avatar_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            avatar_url = url_for('uploaded_file', filename=filename)
        if not (name and email and password and role):
            flash("Please complete all fields", "warning")
            return redirect(url_for("signup"))
        existing = db.get_user_by_email(email)
        if existing:
            flash("Email already registered", "warning")
            return redirect(url_for("login"))
        db.create_user(name, email, password, role, avatar_url)
        flash("Account created! Please log in :)", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out", "info")
    return redirect(url_for("index"))

@app.route("/settings", methods=["GET", "POST"])
def settings():
    user = logged_in_user()
    if not user:
        flash("Please log in", "warning")
        return redirect(url_for("login"))
    current = db.get_user_by_id(user["id"])
    if request.method == "POST":
        # Update profile fields
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        avatar_file = request.files.get("avatar")
        avatar_url = current[5]
        if avatar_file and allowed_file(avatar_file.filename):
            filename = secure_filename(f"{user['id']}_{avatar_file.filename}")
            avatar_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            avatar_url = url_for('uploaded_file', filename=filename)
        try:
            db.update_user(user["id"], name=name or None, email=email or None, password=password or None, avatar=avatar_url)
            updated = db.get_user_by_id(user["id"])
            session["user"] = {
                "id": updated[0], "name": updated[1], "email": updated[2],
                "role": updated[4], "avatar": updated[5]
            }
            flash("Settings updated", "success")
        except Exception as e:
            flash("Error updating settings: " + str(e), "danger")
        return redirect(url_for("settings"))
    return render_template("settings.html", user=current)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- CLASSES ---
@app.route("/classes")
def classes():
    user = logged_in_user()
    if not user:
        flash("Please log in", "warning")
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
            db.enroll_student(c[0], user["id"])
            flash(f"Joined class '{c[1]}'", "success")
            return redirect(url_for("classes"))
    return render_template("join_class.html", user=user)

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
    teacher = db.get_user_by_id(c[3])
    students = db.list_students_in_class(class_id)
    messages = db.list_class_messages(class_id, limit=200)
    assignments = db.get_assignments_for_class(class_id)
    enrolled = (user["role"] == "teacher" and user["id"] == c[3]) or db.is_student_enrolled(class_id, user["id"])
    return render_template("class_detail.html",
                           class_row=c, teacher=teacher, students=students,
                           messages=messages, user=user, enrolled=enrolled, assignments=assignments)

@app.route("/class/<int:class_id>/edit", methods=["GET", "POST"])
def edit_class(class_id):
    user = logged_in_user()
    if not user or user["role"] != "teacher":
        flash("Not authorized", "danger")
        return redirect(url_for("classes"))
    c = db.get_class_by_id(class_id)
    if not c or c[3] != user["id"]:
        flash("You don’t own this class", "danger")
        return redirect(url_for("classes"))
    if request.method == "POST":
        className = request.form.get("className") or None
        description = request.form.get("description") or None
        db.update_class(class_id, className, description)
        flash("Class updated", "success")
        return redirect(url_for("class_detail", class_id=class_id))
    return render_template("edit_class.html", class_data=c)

@app.route("/class/<int:class_id>/delete", methods=["POST"])
def delete_class_route(class_id):
    user = logged_in_user()
    if not user or user["role"] != "teacher":
        flash("Not authorized", "danger")
        return redirect(url_for("classes"))
    db.delete_class(class_id, user["id"])
    flash("Class deleted", "success")
    return redirect(url_for("classes"))

@app.route("/class/<int:class_id>/unenroll", methods=["POST"])
def unenroll_class(class_id):
    user = logged_in_user()
    if not user or user["role"] != "student":
        flash("Not authorized", "danger")
        return redirect(url_for("classes"))
    db.unenroll_student(class_id, user["id"])
    flash("You left the class", "info")
    return redirect(url_for("classes"))

# --- CLASS MESSAGES (with image upload) ---
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
    image = request.files.get("image")
    image_url = None
    if image and allowed_file(image.filename):
        filename = secure_filename(f"class{class_id}_{user['id']}_{datetime.utcnow().timestamp()}_{image.filename}")
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_url = url_for('uploaded_file', filename=filename)
    if not content and not image_url:
        flash("Enter a message or attach an image", "warning")
        return redirect(url_for("class_detail", class_id=class_id))
    db.add_class_message(class_id, user["id"], content, image_url)
    flash("Message posted", "success")
    return redirect(url_for("class_detail", class_id=class_id))

# --- ASSIGNMENTS ---
@app.route("/class/<int:class_id>/assignments/new", methods=["GET", "POST"])
def create_assignment(class_id):
    user = logged_in_user()
    if not user or user["role"] != "teacher":
        flash("Only teachers can create assignments", "danger")
        return redirect(url_for("class_detail", class_id=class_id))
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        due = request.form.get("dueDate", "").strip()
        if not (title and due):
            flash("Title and due date required.", "warning")
            return redirect(url_for("create_assignment", class_id=class_id))
        db.create_assignment(class_id, title, description, due)
        flash("Assignment created!", "success")
        return redirect(url_for("class_detail", class_id=class_id))
    return render_template("create_assignment.html", class_id=class_id)

@app.route("/assignment/<int:assignment_id>")
def assignment_detail(assignment_id):
    user = logged_in_user()
    assignment = db.get_assignment_by_id(assignment_id)
    if not assignment:
        flash("Assignment not found", "danger")
        return redirect(url_for("classes"))
    c = db.get_class_by_id(assignment[1])
    submissions = db.get_submissions_for_assignment(assignment_id)
    my_submission = None
    if user and user["role"] == "student":
        my_submission = db.get_submission_by_student(assignment_id, user["id"])
    return render_template("assignment_detail.html",
                           assignment=assignment, class_row=c,
                           submissions=submissions, my_submission=my_submission, user=user)

@app.route("/assignment/<int:assignment_id>/submit", methods=["POST"])
def submit_assignment(assignment_id):
    user = logged_in_user()
    if not user or user["role"] != "student":
        flash("Only students can submit.", "danger")
        return redirect(url_for("assignment_detail", assignment_id=assignment_id))
    file = request.files.get("file")
    if not file or not allowed_file(file.filename):
        flash("Invalid or no file uploaded.", "danger")
        return redirect(url_for("assignment_detail", assignment_id=assignment_id))
    filename = secure_filename(f"assignment{assignment_id}_student{user['id']}_{datetime.utcnow().timestamp()}_{file.filename}")
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    file_url = url_for('uploaded_file', filename=filename)
    db.submit_assignment(assignment_id, user["id"], file_url)
    flash("Submitted!", "success")
    return redirect(url_for("assignment_detail", assignment_id=assignment_id))

@app.route("/submission/<int:submission_id>/grade", methods=["POST"])
def grade_submission(submission_id):
    user = logged_in_user()
    if not user or user["role"] != "teacher":
        flash("Only teachers can grade.", "danger")
        return redirect(url_for("classes"))
    grade = request.form.get("grade", "").strip()
    feedback = request.form.get("feedback", "").strip()
    db.grade_submission(submission_id, grade, feedback)
    flash("Graded!", "success")
    # Redirect back to assignment page (find assignmentID)
    # For security, just redirect to /classes if not found
    return redirect(request.referrer or url_for("classes"))

# --- DMs AND GROUP CHATS ---
@app.route("/inbox")
def inbox():
    user = logged_in_user()
    if not user:
        flash("Please log in", "warning")
        return redirect(url_for("login"))
    threads = db.get_threads_for_user(user["id"])
    return render_template("inbox.html", user=user, threads=threads)

@app.route("/inbox/new", methods=["GET", "POST"])
def new_dm():
    user = logged_in_user()
    if not user:
        flash("Please log in", "warning")
        return redirect(url_for("login"))
    if request.method == "POST":
        is_group = bool(request.form.get("isGroup"))
        thread_name = request.form.get("threadName") if is_group else None
        raw_participants = request.form.get("participants")  # will be "1,18" or just "1"
        if raw_participants:
            participant_ids = [int(uid) for uid in raw_participants.split(",") if uid.strip()]
        else:
            participant_ids = []
        if user["id"] not in participant_ids:
            participant_ids.append(user["id"])
        thread_id = db.create_dm_thread(participant_ids, isGroup=is_group, threadName=thread_name, createdBy=user["id"])
        return redirect(url_for("dm_thread", thread_id=thread_id))
    return render_template("new_dm.html", user=user)

@app.route("/search_users")
def search_users():
    query = request.args.get("q", "").strip()
    if not query:
        return {"results": []}
    results = db.search_users_by_name_email(query)
    users_list = [{"id": u[0], "name": u[1], "email": u[2], "avatar": u[3]} for u in results]
    return {"results": users_list}

@app.route("/inbox/<int:thread_id>", methods=["GET", "POST"])
def dm_thread(thread_id):
    user = logged_in_user()
    if not user or not db.user_in_thread(user["id"], thread_id):
        flash("Not authorized.", "danger")
        return redirect(url_for("inbox"))
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        image = request.files.get("image")
        image_url = None
        if image and allowed_file(image.filename):
            filename = secure_filename(f"dm{thread_id}_{user['id']}_{datetime.utcnow().timestamp()}_{image.filename}")
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = url_for('uploaded_file', filename=filename)
        if not content and not image_url:
            flash("Enter a message or attach an image", "warning")
            return redirect(url_for("dm_thread", thread_id=thread_id))
        db.add_dm_message(thread_id, user["id"], content, image_url)
        flash("Sent!", "success")
        return redirect(url_for("dm_thread", thread_id=thread_id))
    messages = db.list_dm_messages(thread_id)
    participants = db.get_thread_participants(thread_id)
    return render_template("dm_thread.html", user=user, messages=messages, participants=participants, thread_id=thread_id)

# --- RUN ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)