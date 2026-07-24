from functools import wraps

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user
)
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from models import User, db


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def role_required(required_role):
    def decorator(view_function):
        @wraps(view_function)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("login"))

            if current_user.role != required_role:
                flash(
                    "You are not authorized to access that page.",
                    "danger"
                )
                return redirect(url_for("dashboard"))

            return view_function(*args, **kwargs)

        return wrapped_view

    return decorator


def get_dashboard_url(user):
    if user.role == "admin":
        return url_for("admin_dashboard")

    if user.role == "staff":
        return url_for("staff_dashboard")

    return url_for("user_dashboard")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return redirect(get_dashboard_url(current_user))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        contact = request.form.get("contact", "").strip()
        role = request.form.get("role", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not contact or not role:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if not password or not confirm_password:
            flash("Password fields cannot be empty.", "danger")
            return redirect(url_for("register"))

        if role not in ["user", "staff"]:
            flash("Invalid account type selected.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash(
                "An account with this email already exists.",
                "danger"
            )
            return redirect(url_for("register"))

        new_user = User(
            name=name,
            email=email,
            contact=contact,
            role=role,
            password_hash=generate_password_hash(password),
            is_approved=(role == "user"),
            is_blacklisted=False
        )

        db.session.add(new_user)
        db.session.commit()

        if role == "staff":
            flash(
                "Staff registration successful. Wait for admin approval.",
                "success"
            )
        else:
            flash(
                "Registration successful. You can now log in.",
                "success"
            )

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user is None:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        if not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        if user.is_blacklisted:
            flash(
                "Your account has been blocked. Contact the administrator.",
                "danger"
            )
            return redirect(url_for("login"))

        if user.role == "staff" and not user.is_approved:
            flash(
                "Your staff account is waiting for admin approval.",
                "warning"
            )
            return redirect(url_for("login"))

        login_user(user)

        flash(f"Welcome, {user.name}!", "success")

        return redirect(get_dashboard_url(user))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash(
        "You have been logged out successfully.",
        "success"
    )
    return redirect(url_for("home"))


@app.route("/admin/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    total_users = User.query.filter_by(role="user").count()
    total_staff = User.query.filter_by(role="staff").count()

    pending_staff = User.query.filter_by(
        role="staff",
        is_approved=False
    ).count()

    blacklisted_users = User.query.filter_by(
        is_blacklisted=True
    ).count()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        pending_staff=pending_staff,
        blacklisted_users=blacklisted_users
    )


@app.route("/staff/dashboard")
@login_required
@role_required("staff")
def staff_dashboard():
    return render_template("staff/dashboard.html")


@app.route("/user/dashboard")
@login_required
@role_required("user")
def user_dashboard():
    return render_template("user/dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)