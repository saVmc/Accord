from flask import Flask, render_template, request, redirect, url_for, session, flash
import database_manager as dbHandler

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions

# Home / Index
@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def index():
    if "user" in session:
        return render_template("index.html", user=session["user"])
    else:
        return render_template("index.html", user=None)

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = dbHandler.get_user_by_email(email)
        if user and user[3] == password:  # user tuple: (id, name, email, password, role)
            session["user"] = {"id": user[0], "name": user[1], "email": user[2], "role": user[4]}
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password", "danger")
    return render_template("login.html")

# Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        existing_user = dbHandler.get_user_by_email(email)
        if existing_user:
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("login"))

        dbHandler.create_user(name, email, password, role)
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

# Teacher creates a class
@app.route("/create_class", methods=["GET", "POST"])
def create_class():
    if "user" not in session or session["user"]["role"] != "teacher":
        flash("Only teachers can create classes.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        className = request.form["className"]
        code = dbHandler.create_class(className, session["user"]["id"])
        flash(f"Class created! Share this code with students: {code}", "success")
        return redirect(url_for("my_classes"))

    return render_template("create_class.html")

# Student joins class with a code
@app.route("/join_class", methods=["GET", "POST"])
def join_class():
    if "user" not in session or session["user"]["role"] != "student":
        flash("Only students can join classes.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        code = request.form["classCode"].upper()
        c = dbHandler.get_class_by_code(code)
        if c:
            dbHandler.enroll_student(c[0], session["user"]["id"])
            flash(f"Joined class {c[1]}!", "success")
            return redirect(url_for("my_classes"))
        else:
            flash("Invalid class code.", "danger")

    return render_template("join_class.html")

# Show all classes for the logged-in user
@app.route("/my_classes")
def my_classes():
    if "user" not in session:
        return redirect(url_for("login"))
    
    classes = dbHandler.list_classes_for_user(session["user"]["id"], session["user"]["role"])
    return render_template("my_classes.html", classes=classes, user=session["user"])
