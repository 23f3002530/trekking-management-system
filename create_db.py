from werkzeug.security import generate_password_hash

from app import app
from models import User, db


with app.app_context():
    db.create_all()

    admin = User.query.filter_by(
        email="admin@trekconnect.com"
    ).first()

    if admin is None:
        admin = User(
            name="System Admin",
            email="admin@trekconnect.com",
            password_hash=generate_password_hash("Admin@123"),
            contact="0000000000",
            role="admin",
            is_approved=True,
            is_blacklisted=False
        )

        db.session.add(admin)
        db.session.commit()

        print("Database created successfully.")
        print("Default admin account created.")
    else:
        print("Database already exists.")
        print("Default admin account already exists.")