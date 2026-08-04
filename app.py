from datetime import date, datetime
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
from models import Booking, StaffProfile, Trek, User, db


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

            
            if current_user.is_blacklisted:

                logout_user()

                flash(
                    "Your account has been blocked. "
                    "Contact the administrator.",
                    "danger"
                )

                return redirect(url_for("login"))

            if current_user.role != required_role:

                flash(
                    "You are not authorized to access that page.",
                    "danger"
                )

                return redirect(url_for("dashboard"))

           
            if required_role == "staff" and not current_user.is_approved:

                logout_user()

                flash(
                    "Your staff account requires admin approval.",
                    "warning"
                )

                return redirect(url_for("login"))

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

            flash(
                "All fields are required.",
                "danger"
            )

            return redirect(url_for("register"))

        if not password or not confirm_password:

            flash(
                "Password fields cannot be empty.",
                "danger"
            )

            return redirect(url_for("register"))

        if role not in ["user", "staff"]:

            flash(
                "Invalid account type selected.",
                "danger"
            )

            return redirect(url_for("register"))

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(url_for("register"))

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect(url_for("register"))

        existing_user = User.query.filter_by(
            email=email
        ).first()

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
        db.session.flush()

        if role == "staff":

            staff_profile = StaffProfile(
                user_id=new_user.id
            )

            db.session.add(staff_profile)

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

        user = User.query.filter_by(
            email=email
        ).first()

        if user is None:

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(url_for("login"))

        if not check_password_hash(
            user.password_hash,
            password
        ):

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(url_for("login"))

        if user.is_blacklisted:

            flash(
                "Your account has been blocked. "
                "Contact the administrator.",
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

        flash(
            f"Welcome, {user.name}!",
            "success"
        )

        return redirect(get_dashboard_url(user))

    return render_template("login.html")






@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not email or not new_password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for("forgot_password"))

        if len(new_password) < 6:
            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )
            return redirect(url_for("forgot_password"))

        if new_password != confirm_password:
            flash(
                "New password and confirm password do not match.",
                "danger"
            )
            return redirect(url_for("forgot_password"))

        user = User.query.filter(
            db.func.lower(User.email) == email
        ).first()

        if user is None:
            flash(
                "No account was found with that email address.",
                "danger"
            )
            return redirect(url_for("forgot_password"))

        if user.role == "admin":
            flash(
                "Admin password cannot be reset from this page.",
                "danger"
            )
            return redirect(url_for("forgot_password"))

        user.password_hash = generate_password_hash(
            new_password
        )

        db.session.commit()

        flash(
            "Password reset successfully. You can now log in.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("forgot_password.html")


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

    total_users = User.query.filter_by(
        role="user"
    ).count()

    total_staff = User.query.filter_by(
        role="staff"
    ).count()

    pending_staff = User.query.filter_by(
        role="staff",
        is_approved=False,
        is_blacklisted=False
    ).count()

    blacklisted_users = User.query.filter_by(
        is_blacklisted=True
    ).count()

    total_treks = Trek.query.count()

    total_bookings = Booking.query.count()

    open_treks = Trek.query.filter_by(
        status="Open"
    ).count()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        pending_staff=pending_staff,
        blacklisted_users=blacklisted_users,
        total_treks=total_treks,
        total_bookings=total_bookings,
        open_treks=open_treks
    )




@app.route("/admin/staff")
@login_required
@role_required("admin")
def manage_staff():

    
    search = request.args.get(
        "search",
        ""
    ).strip()

                                      
    query = User.query.filter_by(
        role="staff"
    )

                                      
    if search:

        if search.isdigit():

            query = query.filter(
                db.or_(
                    User.id == int(search),
                    User.name.ilike(f"%{search}%")
                )
            )

        else:

            query = query.filter(
                User.name.ilike(f"%{search}%")
            )

                                   
    staff_members = (
        query
        .order_by(User.created_at.desc())
        .all()
    )

    return render_template(
        "admin/staff_management.html",
        staff_members=staff_members,
        search=search
    )


@app.route(
    "/admin/staff/<int:staff_id>/approve",
    methods=["POST"]
)
@login_required
@role_required("admin")
def approve_staff(staff_id):

    staff = db.get_or_404(User, staff_id)

    if staff.role != "staff":

        flash(
            "The selected account is not a staff account.",
            "danger"
        )

        return redirect(url_for("manage_staff"))

    if staff.is_blacklisted:

        flash(
            "A blocked staff account cannot be approved.",
            "warning"
        )

        return redirect(url_for("manage_staff"))

    if staff.is_approved:

        flash(
            "This staff account is already approved.",
            "info"
        )

        return redirect(url_for("manage_staff"))

    staff.is_approved = True
    db.session.commit()

    flash(
        f"{staff.name}'s staff account has been approved.",
        "success"
    )

    return redirect(url_for("manage_staff"))


@app.route(
    "/admin/staff/<int:staff_id>/revoke",
    methods=["POST"]
)
@login_required
@role_required("admin")
def revoke_staff(staff_id):

    staff = db.get_or_404(User, staff_id)

    if staff.role != "staff":

        flash(
            "The selected account is not a staff account.",
            "danger"
        )

        return redirect(url_for("manage_staff"))

    if not staff.is_approved:

        flash(
            "This staff account is already pending approval.",
            "info"
        )

        return redirect(url_for("manage_staff"))

    staff.is_approved = False
    db.session.commit()

    flash(
        f"Approval has been revoked for {staff.name}.",
        "warning"
    )

    return redirect(url_for("manage_staff"))


@app.route(
    "/admin/staff/<int:staff_id>/block",
    methods=["POST"]
)
@login_required
@role_required("admin")
def block_staff(staff_id):

    staff = db.get_or_404(User, staff_id)

    if staff.role != "staff":

        flash(
            "The selected account is not a staff account.",
            "danger"
        )

        return redirect(url_for("manage_staff"))

    if staff.is_blacklisted:

        flash(
            "This staff account is already blocked.",
            "info"
        )

        return redirect(url_for("manage_staff"))

    staff.is_blacklisted = True
    staff.is_approved = False

    db.session.commit()

    flash(
        f"{staff.name}'s account has been blocked.",
        "danger"
    )

    return redirect(url_for("manage_staff"))


@app.route(
    "/admin/staff/<int:staff_id>/unblock",
    methods=["POST"]
)
@login_required
@role_required("admin")
def unblock_staff(staff_id):

    staff = db.get_or_404(User, staff_id)

    if staff.role != "staff":

        flash(
            "The selected account is not a staff account.",
            "danger"
        )

        return redirect(url_for("manage_staff"))

    if not staff.is_blacklisted:

        flash(
            "This staff account is not blocked.",
            "info"
        )

        return redirect(url_for("manage_staff"))

    staff.is_blacklisted = False
    db.session.commit()

    flash(
        f"{staff.name}'s account has been unblocked. "
        "The account still requires approval.",
        "success"
    )

    return redirect(url_for("manage_staff"))


                                                    
                       
                                                    

@app.route("/admin/users")
@login_required
@role_required("admin")
def manage_users():

                               
    search = request.args.get(
        "search",
        ""
    ).strip()

                                         
    query = User.query.filter_by(
        role="user"
    )

                                       
    if search:

        if search.isdigit():

            query = query.filter(
                db.or_(
                    User.id == int(search),
                    User.name.ilike(f"%{search}%")
                )
            )

        else:

            query = query.filter(
                User.name.ilike(f"%{search}%")
            )

                                   
    users = (
        query
        .order_by(User.created_at.desc())
        .all()
    )

    return render_template(
        "admin/user_management.html",
        users=users,
        search=search
    )


@app.route(
    "/admin/users/<int:user_id>/block",
    methods=["POST"]
)
@login_required
@role_required("admin")
def block_user(user_id):

    user = db.get_or_404(User, user_id)

    if user.role != "user":

        flash(
            "The selected account is not a trekker account.",
            "danger"
        )

        return redirect(url_for("manage_users"))

    if user.is_blacklisted:

        flash(
            "This trekker account is already blocked.",
            "info"
        )

        return redirect(url_for("manage_users"))

    user.is_blacklisted = True
    db.session.commit()

    flash(
        f"{user.name}'s account has been blocked.",
        "danger"
    )

    return redirect(url_for("manage_users"))


@app.route(
    "/admin/users/<int:user_id>/unblock",
    methods=["POST"]
)
@login_required
@role_required("admin")
def unblock_user(user_id):

    user = db.get_or_404(User, user_id)

    if user.role != "user":

        flash(
            "The selected account is not a trekker account.",
            "danger"
        )

        return redirect(url_for("manage_users"))

    if not user.is_blacklisted:

        flash(
            "This trekker account is not blocked.",
            "info"
        )

        return redirect(url_for("manage_users"))

    user.is_blacklisted = False
    db.session.commit()

    flash(
        f"{user.name}'s account has been unblocked.",
        "success"
    )

    return redirect(url_for("manage_users"))


                                                    
                       
                                                    

@app.route("/admin/treks")
@login_required
@role_required("admin")
def manage_treks():

                                               
    search = request.args.get(
        "search",
        ""
    ).strip()

    difficulty = request.args.get(
        "difficulty",
        ""
    ).strip()

    trek_status = request.args.get(
        "trek_status",
        ""
    ).strip()

                          
    query = Trek.query

                                    
    if search:

        if search.isdigit():

            query = query.filter(
                db.or_(
                    Trek.name.ilike(f"%{search}%"),
                    Trek.id == int(search)
                )
            )

        else:

            query = query.filter(
                Trek.name.ilike(f"%{search}%")
            )

                          
    if difficulty in [
        "Easy",
        "Moderate",
        "Hard"
    ]:

        query = query.filter(
            Trek.difficulty == difficulty
        )

                           
    if trek_status in [
        "Open",
        "Closed",
        "Started",
        "Completed"
    ]:

        query = query.filter(
            Trek.status == trek_status
        )

                                      
    treks = (
        query
        .order_by(Trek.start_date.asc())
        .all()
    )

    return render_template(
        "admin/trek_management.html",
        treks=treks,
        search=search,
        difficulty=difficulty,
        trek_status=trek_status
    )


@app.route("/admin/treks/add", methods=["GET", "POST"])
@login_required
@role_required("admin")
def add_trek():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        difficulty = request.form.get("difficulty", "").strip()
        duration = request.form.get("duration", "").strip()
        maximum_slots = request.form.get(
            "maximum_slots",
            ""
        ).strip()

        start_date_text = request.form.get(
            "start_date",
            ""
        ).strip()

        end_date_text = request.form.get(
            "end_date",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        if (
            not name
            or not location
            or not difficulty
            or not duration
            or not maximum_slots
            or not start_date_text
            or not end_date_text
        ):

            flash(
                "Please fill in all required fields.",
                "danger"
            )

            return redirect(url_for("add_trek"))

        if difficulty not in ["Easy", "Moderate", "Hard"]:

            flash(
                "Please select a valid difficulty level.",
                "danger"
            )

            return redirect(url_for("add_trek"))

        try:

            duration = int(duration)
            maximum_slots = int(maximum_slots)

        except ValueError:

            flash(
                "Duration and maximum slots must be valid numbers.",
                "danger"
            )

            return redirect(url_for("add_trek"))

        if duration <= 0:

            flash(
                "Duration must be greater than zero.",
                "danger"
            )

            return redirect(url_for("add_trek"))

        if maximum_slots <= 0:

            flash(
                "Maximum slots must be greater than zero.",
                "danger"
            )

            return redirect(url_for("add_trek"))

        try:

            start_date = datetime.strptime(
                start_date_text,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                end_date_text,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Please enter valid trek dates.",
                "danger"
            )

            return redirect(url_for("add_trek"))

        if end_date < start_date:

            flash(
                "End date cannot be earlier than the start date.",
                "danger"
            )

            return redirect(url_for("add_trek"))

        existing_trek = Trek.query.filter_by(
            name=name,
            start_date=start_date
        ).first()

        if existing_trek:

            flash(
                "A trek with this name and start date already exists.",
                "warning"
            )

            return redirect(url_for("add_trek"))

        new_trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            maximum_slots=maximum_slots,
            available_slots=maximum_slots,
            status="Open",
            start_date=start_date,
            end_date=end_date,
            description=description
        )

        db.session.add(new_trek)
        db.session.commit()

        flash(
            f"{new_trek.name} has been created successfully.",
            "success"
        )

        return redirect(url_for("manage_treks"))

    return render_template("admin/add_trek.html")


@app.route(
    "/admin/treks/<int:trek_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@role_required("admin")
def edit_trek(trek_id):

    trek = db.get_or_404(Trek, trek_id)

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        difficulty = request.form.get("difficulty", "").strip()
        duration = request.form.get("duration", "").strip()

        maximum_slots = request.form.get(
            "maximum_slots",
            ""
        ).strip()

        start_date_text = request.form.get(
            "start_date",
            ""
        ).strip()

        end_date_text = request.form.get(
            "end_date",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        if (
            not name
            or not location
            or not difficulty
            or not duration
            or not maximum_slots
            or not start_date_text
            or not end_date_text
        ):

            flash(
                "Please fill in all required fields.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_trek",
                    trek_id=trek.id
                )
            )

        if difficulty not in ["Easy", "Moderate", "Hard"]:

            flash(
                "Please select a valid difficulty level.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_trek",
                    trek_id=trek.id
                )
            )

        try:

            duration = int(duration)
            new_maximum_slots = int(maximum_slots)

        except ValueError:

            flash(
                "Duration and maximum slots must be valid numbers.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_trek",
                    trek_id=trek.id
                )
            )

        if duration <= 0:

            flash(
                "Duration must be greater than zero.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_trek",
                    trek_id=trek.id
                )
            )

        if new_maximum_slots <= 0:

            flash(
                "Maximum slots must be greater than zero.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_trek",
                    trek_id=trek.id
                )
            )

        booked_slots = (
            trek.maximum_slots - trek.available_slots
        )

        if new_maximum_slots < booked_slots:

            flash(
                "Maximum slots cannot be less than the number "
                "of existing bookings.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_trek",
                    trek_id=trek.id
                )
            )

        try:

            start_date = datetime.strptime(
                start_date_text,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                end_date_text,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Please enter valid trek dates.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_trek",
                    trek_id=trek.id
                )
            )

        if end_date < start_date:

            flash(
                "End date cannot be earlier than the start date.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_trek",
                    trek_id=trek.id
                )
            )

        duplicate_trek = (
            Trek.query
            .filter(
                Trek.id != trek.id,
                Trek.name == name,
                Trek.start_date == start_date
            )
            .first()
        )

        if duplicate_trek:

            flash(
                "Another trek with this name and start date already exists.",
                "warning"
            )

            return redirect(
                url_for(
                    "edit_trek",
                    trek_id=trek.id
                )
            )

        trek.name = name
        trek.location = location
        trek.difficulty = difficulty
        trek.duration = duration
        trek.maximum_slots = new_maximum_slots

        trek.available_slots = (
            new_maximum_slots - booked_slots
        )

        trek.start_date = start_date
        trek.end_date = end_date
        trek.description = description

        db.session.commit()

        flash(
            f"{trek.name} has been updated successfully.",
            "success"
        )

        return redirect(url_for("manage_treks"))

    return render_template(
        "admin/edit_trek.html",
        trek=trek
    )


@app.route(
    "/admin/treks/<int:trek_id>/delete",
    methods=["POST"]
)
@login_required
@role_required("admin")
def delete_trek(trek_id):

    trek = db.get_or_404(Trek, trek_id)

    existing_booking = Booking.query.filter_by(
        trek_id=trek.id
    ).first()

    if existing_booking:

        flash(
            "This trek cannot be deleted because bookings already exist.",
            "danger"
        )

        return redirect(url_for("manage_treks"))

    trek_name = trek.name

    db.session.delete(trek)
    db.session.commit()

    flash(
        f"{trek_name} has been deleted successfully.",
        "success"
    )

    return redirect(url_for("manage_treks"))


@app.route(
    "/admin/treks/<int:trek_id>/toggle",
    methods=["POST"]
)
@login_required
@role_required("admin")
def toggle_trek_status(trek_id):

    trek = db.get_or_404(Trek, trek_id)

    if trek.status == "Open":

        trek.status = "Closed"

        flash(
            f"Registration for {trek.name} has been closed.",
            "warning"
        )

    else:

        if trek.status == "Completed":

            flash(
                "A completed trek cannot be reopened.",
                "warning"
            )

            return redirect(url_for("manage_treks"))

        if trek.available_slots <= 0:

            flash(
                "This trek cannot be opened because no slots are available.",
                "danger"
            )

            return redirect(url_for("manage_treks"))

        trek.status = "Open"

        flash(
            f"Registration for {trek.name} has been opened.",
            "success"
        )

    db.session.commit()

    return redirect(url_for("manage_treks"))


                                                    
                      
                                                    

@app.route(
    "/admin/treks/<int:trek_id>/assign",
    methods=["GET", "POST"]
)
@login_required
@role_required("admin")
def assign_staff(trek_id):

    trek = db.get_or_404(Trek, trek_id)

    staff_members = (
        User.query
        .filter_by(
            role="staff",
            is_approved=True,
            is_blacklisted=False
        )
        .order_by(User.name.asc())
        .all()
    )

    if request.method == "POST":

        staff_id = request.form.get("staff_id", "").strip()

        if not staff_id:

            flash(
                "Please select a staff member.",
                "danger"
            )

            return redirect(
                url_for(
                    "assign_staff",
                    trek_id=trek.id
                )
            )

        try:
            staff_id = int(staff_id)

        except ValueError:

            flash(
                "Invalid staff member selected.",
                "danger"
            )

            return redirect(
                url_for(
                    "assign_staff",
                    trek_id=trek.id
                )
            )

        staff = db.session.get(User, staff_id)

        if staff is None or staff.role != "staff":

            flash(
                "The selected account is not a valid staff account.",
                "danger"
            )

            return redirect(
                url_for(
                    "assign_staff",
                    trek_id=trek.id
                )
            )

        if not staff.is_approved:

            flash(
                "Only approved staff members can be assigned.",
                "warning"
            )

            return redirect(
                url_for(
                    "assign_staff",
                    trek_id=trek.id
                )
            )

        if staff.is_blacklisted:

            flash(
                "A blocked staff member cannot be assigned.",
                "warning"
            )

            return redirect(
                url_for(
                    "assign_staff",
                    trek_id=trek.id
                )
            )

        trek.assigned_staff_id = staff.id
        db.session.commit()

        flash(
            f"{staff.name} has been assigned to {trek.name}.",
            "success"
        )

        return redirect(url_for("manage_treks"))

    return render_template(
        "admin/assign_staff.html",
        trek=trek,
        staff_members=staff_members
    )

             
@app.route("/admin/treks/<int:trek_id>/remove_staff", methods=["POST"])
@login_required
@role_required("admin")
def remove_staff(trek_id):

    trek = db.get_or_404(Trek, trek_id)

    if trek.assigned_staff is None:
        flash("No staff member is assigned to this trek.", "info")
        return redirect(url_for("manage_treks"))

    staff_name = trek.assigned_staff.name

    trek.assigned_staff_id = None
    db.session.commit()

    flash(
        f"{staff_name} has been removed from {trek.name}.",
        "success"
    )

    return redirect(url_for("manage_treks"))
                                                    
                 
                                                    

@app.route("/staff/dashboard")
@login_required
@role_required("staff")
def staff_dashboard():

    assigned_treks = (
        Trek.query
        .filter_by(assigned_staff_id=current_user.id)
        .order_by(Trek.start_date.asc())
        .all()
    )

    upcoming = sum(
        1 for trek in assigned_treks
        if trek.start_date >= date.today()
        and trek.status != "Completed"
    )

    completed = sum(
        1 for trek in assigned_treks
        if trek.status == "Completed"
    )

                                           
                                                                 
                                                                    
    trek_participant_data = []

    for trek in assigned_treks:

        participant_count = Booking.query.filter(
            Booking.trek_id == trek.id,
            Booking.status != "Cancelled"
        ).count()

        trek_participant_data.append({
            "trek": trek,
            "participant_count": participant_count
        })

    return render_template(
        "staff/dashboard.html",
        assigned_count=len(assigned_treks),
        upcoming_count=upcoming,
        completed_count=completed,
        trek_participant_data=trek_participant_data
    )

@app.route("/staff/treks")
@login_required
@role_required("staff")
def assigned_treks():

    treks = (
        Trek.query
        .filter_by(assigned_staff_id=current_user.id)
        .order_by(Trek.start_date)
        .all()
    )

    return render_template(
        "staff/assigned_treks.html",
        treks=treks
    )

                                                    
                            
                                                    

@app.route(
    "/staff/treks/<int:trek_id>/manage",
    methods=["GET", "POST"]
)
@login_required
@role_required("staff")
def staff_manage_trek(trek_id):

    trek = db.get_or_404(Trek, trek_id)

    if trek.assigned_staff_id != current_user.id:
        flash("You are not authorized to manage this trek.", "danger")
        return redirect(url_for("assigned_treks"))

    if trek.status not in ["Open", "Closed"]:
        flash(
            "A started or completed trek cannot be modified.",
            "warning"
        )
        return redirect(url_for("assigned_treks"))

    if request.method == "POST":

        available_slots_text = request.form.get(
            "available_slots", ""
        ).strip()

        trek_status = request.form.get(
            "status", ""
        ).strip()

        if not available_slots_text or not trek_status:
            flash(
                "Available slots and trek status are required.",
                "danger"
            )
            return redirect(
                url_for("staff_manage_trek", trek_id=trek.id)
            )

        try:
            available_slots = int(available_slots_text)
        except ValueError:
            flash(
                "Available slots must be a valid whole number.",
                "danger"
            )
            return redirect(
                url_for("staff_manage_trek", trek_id=trek.id)
            )

        if available_slots < 0:
            flash("Available slots cannot be negative.", "danger")
            return redirect(
                url_for("staff_manage_trek", trek_id=trek.id)
            )

        if available_slots > trek.maximum_slots:
            flash(
                "Available slots cannot be greater than maximum slots.",
                "danger"
            )
            return redirect(
                url_for("staff_manage_trek", trek_id=trek.id)
            )

        confirmed_count = Booking.query.filter_by(
            trek_id=trek.id,
            status="Confirmed"
        ).count()

        maximum_available_slots = (
            trek.maximum_slots - confirmed_count
        )

        if available_slots > maximum_available_slots:
            flash(
                "Available slots cannot exceed the remaining capacity "
                "after existing bookings.",
                "danger"
            )
            return redirect(
                url_for("staff_manage_trek", trek_id=trek.id)
            )

        if trek_status not in ["Open", "Closed"]:
            flash("Please select a valid trek status.", "danger")
            return redirect(
                url_for("staff_manage_trek", trek_id=trek.id)
            )

        if available_slots == 0 and trek_status == "Open":
            flash(
                "A trek with zero available slots cannot be Open.",
                "warning"
            )
            return redirect(
                url_for("staff_manage_trek", trek_id=trek.id)
            )

        trek.available_slots = available_slots
        trek.status = trek_status
        db.session.commit()

        flash(
            f"{trek.name} has been updated successfully.",
            "success"
        )
        return redirect(url_for("assigned_treks"))

    return render_template(
        "staff/manage_trek.html",
        trek=trek
    )


@app.route("/staff/treks/<int:trek_id>/participants")
@login_required
@role_required("staff")
def view_participants(trek_id):

    trek = db.get_or_404(Trek, trek_id)

    if trek.assigned_staff_id != current_user.id:

        flash(
            "You are not assigned to this trek.",
            "danger"
        )

        return redirect(url_for("assigned_treks"))

    bookings = (
        Booking.query
        .filter(
            Booking.trek_id == trek.id,
            Booking.status.in_(["Confirmed", "Completed"])
        )
        .all()
    )

    return render_template(
        "staff/participants.html",
        trek=trek,
        bookings=bookings
    )


                                                    
                             
                                                    

@app.route(
    "/staff/bookings/<int:booking_id>/attendance/<attendance_status>",
    methods=["POST"]
)
@login_required
@role_required("staff")
def mark_attendance(booking_id, attendance_status):

    booking = db.get_or_404(Booking, booking_id)
    trek = booking.trek

                                                                     
    if trek.assigned_staff_id != current_user.id:

        flash(
            "You are not authorized to mark attendance for this trek.",
            "danger"
        )

        return redirect(url_for("assigned_treks"))

                                                          
    if booking.status != "Confirmed":

        flash(
            "Attendance can only be marked for confirmed participants.",
            "warning"
        )

        return redirect(
            url_for(
                "view_participants",
                trek_id=trek.id
            )
        )

                                                         
    if attendance_status not in ["Present", "Absent"]:

        flash(
            "Invalid attendance status.",
            "danger"
        )

        return redirect(
            url_for(
                "view_participants",
                trek_id=trek.id
            )
        )

    booking.attendance_status = attendance_status
    db.session.commit()

    flash(
        f"{booking.user.name} has been marked {attendance_status}.",
        "success"
    )

    return redirect(
        url_for(
            "view_participants",
            trek_id=trek.id
        )
    )

                                                    
                         
                                                    

@app.route(
    "/staff/treks/<int:trek_id>/start",
    methods=["POST"]
)
@login_required
@role_required("staff")
def start_trek(trek_id):

    trek = db.get_or_404(Trek, trek_id)

    if trek.assigned_staff_id != current_user.id:
        flash(
            "You are not authorized to start this trek.",
            "danger"
        )
        return redirect(url_for("assigned_treks"))

    if trek.status == "Completed":
        flash(
            "This trek has already been completed.",
            "warning"
        )
        return redirect(url_for("assigned_treks"))

    if trek.status == "Started":
        flash(
            "This trek has already been started.",
            "warning"
        )
        return redirect(url_for("assigned_treks"))

    if trek.status not in ["Open", "Closed"]:
        flash(
            "This trek cannot be started from its current status.",
            "danger"
        )
        return redirect(url_for("assigned_treks"))

    trek.status = "Started"
    db.session.commit()

    flash(
        f"{trek.name} has been marked as started.",
        "success"
    )
    return redirect(url_for("assigned_treks"))


                                                    
                       
                                                    

@app.route(
    "/staff/treks/<int:trek_id>/complete",
    methods=["POST"]
)
@login_required
@role_required("staff")
def complete_trek(trek_id):

    trek = db.get_or_404(Trek, trek_id)

    if trek.assigned_staff_id != current_user.id:

        flash(
            "You are not authorized to complete this trek.",
            "danger"
        )

        return redirect(url_for("assigned_treks"))

    if trek.status == "Completed":

        flash(
            "This trek has already been marked as completed.",
            "info"
        )

        return redirect(url_for("assigned_treks"))

    if trek.status != "Started":

        flash(
            "The trek must be marked as started before it can be completed.",
            "warning"
        )

        return redirect(url_for("assigned_treks"))

    confirmed_bookings = Booking.query.filter_by(
        trek_id=trek.id,
        status="Confirmed"
    ).all()

    pending_attendance = [
        booking
        for booking in confirmed_bookings
        if booking.attendance_status == "Pending"
    ]

    if pending_attendance:

        flash(
            "Please mark attendance for all participants "
            "before completing the trek.",
            "warning"
        )

        return redirect(
            url_for(
                "view_participants",
                trek_id=trek.id
            )
        )

                                                            
                                                                     
    trek.status = "Completed"

    for booking in confirmed_bookings:
        booking.status = "Completed"

    db.session.commit()

    flash(
        f"{trek.name} has been marked as completed.",
        "success"
    )

    return redirect(url_for("assigned_treks"))


                                                    
                          
                                                    

@app.route("/admin/bookings")
@login_required
@role_required("admin")
def manage_bookings():

                                               
    search = request.args.get(
        "search",
        ""
    ).strip()

    booking_status = request.args.get(
        "booking_status",
        ""
    ).strip()

    attendance_status = request.args.get(
        "attendance_status",
        ""
    ).strip()

                             
    query = Booking.query

                                    
                                
    if search:

        query = (
            query
            .join(User, Booking.user_id == User.id)
            .join(Trek, Booking.trek_id == Trek.id)
            .filter(
                db.or_(
                    User.name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    Trek.name.ilike(f"%{search}%"),
                    Trek.location.ilike(f"%{search}%")
                )
            )
        )

                              
    if booking_status in ["Confirmed", "Cancelled", "Completed"]:

        query = query.filter(
            Booking.status == booking_status
        )

                                 
    if attendance_status in [
        "Pending",
        "Present",
        "Absent"
    ]:

        query = query.filter(
            Booking.attendance_status == attendance_status
        )

                           
    bookings = (
        query
        .order_by(Booking.booking_date.desc())
        .all()
    )

    return render_template(
        "admin/booking_management.html",
        bookings=bookings,
        search=search,
        booking_status=booking_status,
        attendance_status=attendance_status
    )

                                                    
               
                                                    

@app.route("/admin/reports")
@login_required
@role_required("admin")
def admin_reports():

    total_treks = Trek.query.count()

    completed_treks = Trek.query.filter_by(
        status="Completed"
    ).count()

    open_treks = Trek.query.filter_by(
        status="Open"
    ).count()

    closed_treks = Trek.query.filter_by(
        status="Closed"
    ).count()

    total_confirmed_bookings = Booking.query.filter(
        Booking.status.in_(["Confirmed", "Completed"])
    ).count()

    total_cancelled_bookings = Booking.query.filter_by(
        status="Cancelled"
    ).count()

    total_present = Booking.query.filter(
        Booking.status.in_(["Confirmed", "Completed"]),
        Booking.attendance_status == "Present"
    ).count()

    total_absent = Booking.query.filter(
        Booking.status.in_(["Confirmed", "Completed"]),
        Booking.attendance_status == "Absent"
    ).count()

    total_pending_attendance = Booking.query.filter(
        Booking.status.in_(["Confirmed", "Completed"]),
        Booking.attendance_status == "Pending"
    ).count()

    treks = (
        Trek.query
        .order_by(Trek.start_date.desc())
        .all()
    )

    trek_reports = []

    for trek in treks:

        confirmed_bookings = Booking.query.filter(
            Booking.trek_id == trek.id,
            Booking.status.in_(["Confirmed", "Completed"])
        ).all()

        confirmed_count = len(confirmed_bookings)

        present_count = sum(
            1
            for booking in confirmed_bookings
            if booking.attendance_status == "Present"
        )

        absent_count = sum(
            1
            for booking in confirmed_bookings
            if booking.attendance_status == "Absent"
        )

        pending_count = sum(
            1
            for booking in confirmed_bookings
            if booking.attendance_status == "Pending"
        )

        trek_reports.append(
            {
                "trek": trek,
                "confirmed_count": confirmed_count,
                "present_count": present_count,
                "absent_count": absent_count,
                "pending_count": pending_count
            }
        )

    return render_template(
        "admin/reports.html",
        total_treks=total_treks,
        completed_treks=completed_treks,
        open_treks=open_treks,
        closed_treks=closed_treks,
        total_confirmed_bookings=total_confirmed_bookings,
        total_cancelled_bookings=total_cancelled_bookings,
        total_present=total_present,
        total_absent=total_absent,
        total_pending_attendance=total_pending_attendance,
        trek_reports=trek_reports
    )


                                                    
                                 
                                                    

@app.route("/user/dashboard")
@login_required
@role_required("user")
def user_dashboard():
    total_bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).count()

    active_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        status="Confirmed"
    ).count()

    available_treks_count = (
        Trek.query
        .filter(
            Trek.status == "Open",
            Trek.available_slots > 0,
            Trek.start_date >= date.today()
        )
        .count()
    )

    return render_template(
        "user/dashboard.html",
        total_bookings=total_bookings,
        active_bookings=active_bookings,
        available_treks_count=available_treks_count
    )


                                                    
                   
                                                    

@app.route(
    "/user/profile/edit",
    methods=["GET", "POST"]
)
@login_required
@role_required("user")
def edit_profile():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        contact = request.form.get(
            "contact",
            ""
        ).strip()

        if not name or not email or not contact:

            flash(
                "Name, email and contact number are required.",
                "danger"
            )

            return redirect(url_for("edit_profile"))

                                                                    
        existing_user = (
            User.query
            .filter(
                User.email == email,
                User.id != current_user.id
            )
            .first()
        )

        if existing_user:

            flash(
                "That email address is already registered to another account.",
                "danger"
            )

            return redirect(url_for("edit_profile"))

        current_user.name = name
        current_user.email = email
        current_user.contact = contact

        db.session.commit()

        flash(
            "Your profile has been updated successfully.",
            "success"
        )

        return redirect(url_for("user_dashboard"))

    return render_template(
        "user/edit_profile.html"
    )


@app.route("/user/treks")
@login_required
@role_required("user")
def available_treks():

    search = request.args.get(
        "search",
        ""
    ).strip()

    location = request.args.get(
        "location",
        ""
    ).strip()

    difficulty = request.args.get(
        "difficulty",
        ""
    ).strip()

                                                               
    query = Trek.query.filter(
        Trek.status == "Open",
        Trek.available_slots > 0,
        Trek.start_date >= date.today()
    )

                                       
    if search:
        query = query.filter(
            Trek.name.ilike(f"%{search}%")
        )

                               
    if location:
        query = query.filter(
            Trek.location.ilike(f"%{location}%")
        )

                        
    if difficulty in [
        "Easy",
        "Moderate",
        "Hard"
    ]:
        query = query.filter(
            Trek.difficulty == difficulty
        )

    treks = (
        query
        .order_by(Trek.start_date.asc())
        .all()
    )

                                                                    
                                              
    bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).all()

    booked_trek_ids = {
        booking.trek_id
        for booking in bookings
        if booking.status != "Cancelled"
    }

    return render_template(
        "user/available_treks.html",
        treks=treks,
        booked_trek_ids=booked_trek_ids,
        search=search,
        location=location,
        difficulty=difficulty
    )


@app.route(
    "/user/treks/<int:trek_id>/book",
    methods=["POST"]
)
@login_required
@role_required("user")
def book_trek(trek_id):
    trek = db.get_or_404(Trek, trek_id)

    if current_user.is_blacklisted:
        flash(
            "Your account is blocked. You cannot book a trek.",
            "danger"
        )
        return redirect(url_for("available_treks"))

    if trek.status != "Open":
        flash(
            "Registration for this trek is currently closed.",
            "warning"
        )
        return redirect(url_for("available_treks"))

    if trek.start_date < date.today():
        flash(
            "This trek has already started.",
            "warning"
        )
        return redirect(url_for("available_treks"))

    if trek.available_slots <= 0:
        flash(
            "No slots are available for this trek.",
            "danger"
        )
        return redirect(url_for("available_treks"))

    existing_booking = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek.id
    ).first()

    if existing_booking and existing_booking.status != "Cancelled":
        flash(
            "You have already booked this trek.",
            "warning"
        )
        return redirect(url_for("available_treks"))

    if existing_booking:
        existing_booking.status = "Confirmed"
        existing_booking.booking_date = datetime.utcnow()
    else:
        new_booking = Booking(
            user_id=current_user.id,
            trek_id=trek.id,
            status="Confirmed"
        )
        db.session.add(new_booking)

    trek.available_slots -= 1

    if trek.available_slots == 0:
        trek.status = "Closed"

    db.session.commit()

    flash(
        f"You have successfully booked {trek.name}.",
        "success"
    )

    return redirect(url_for("my_bookings"))


@app.route("/user/bookings")
@login_required
@role_required("user")
def my_bookings():
    bookings = (
        Booking.query
        .filter_by(user_id=current_user.id)
        .order_by(Booking.booking_date.desc())
        .all()
    )

    return render_template(
        "user/my_bookings.html",
        bookings=bookings
    )


@app.route(
    "/user/bookings/<int:booking_id>/cancel",
    methods=["POST"]
)
@login_required
@role_required("user")
def cancel_booking(booking_id):
    booking = db.get_or_404(Booking, booking_id)

    if booking.user_id != current_user.id:
        flash(
            "You are not authorized to cancel this booking.",
            "danger"
        )
        return redirect(url_for("my_bookings"))

    if booking.status == "Cancelled":
        flash(
            "This booking has already been cancelled.",
            "info"
        )
        return redirect(url_for("my_bookings"))

    trek = booking.trek

    
    if trek.status in ["Started", "Completed"]:
        flash(
            "You cannot cancel a booking after the trek has started.",
            "warning"
        )
        return redirect(url_for("my_bookings"))

    if trek.start_date <= date.today():
        flash(
            "You cannot cancel a booking on or after the trek start date.",
            "warning"
        )
        return redirect(url_for("my_bookings"))

    booking.status = "Cancelled"

    if trek.available_slots < trek.maximum_slots:
        trek.available_slots += 1

    if trek.status == "Closed" and trek.available_slots > 0:
        trek.status = "Open"

    db.session.commit()

    flash(
        f"Your booking for {trek.name} has been cancelled.",
        "success"
    )

    return redirect(url_for("my_bookings"))



if __name__ == "__main__":
    app.run(debug=True)