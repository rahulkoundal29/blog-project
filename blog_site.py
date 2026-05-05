from flask import Flask, render_template, redirect, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

# ------------------ ENV SETUP ------------------
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL", "sqlite:///users.db"
)

# ------------------ DB ------------------
db = SQLAlchemy(app)

# ------------------ LOGIN MANAGER ------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ------------------ USER LOADER ------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------ MODEL ------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/blog")
def blog():
    posts = [
        {
            "title": "Getting Started with Flask",
            "content": "Flask is a lightweight Python web framework...",
            "author": "Admin",
            "created_at": datetime(2026, 4, 10),
        }
    ]
    return render_template("blog.html", posts=posts)


# ------------------ AUTH ------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))

        new_user = User(username=username, email=email, password=password)

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            return "User not found"

        if not check_password_hash(user.password, password):
            return "Wrong password"

        login_user(user)
        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/dashboard")
@login_required
def dashboard():
    return "Welcome! You are logged in"


# ------------------ RUN ------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)