from sqlalchemy import inspect, text

from app import app
from models import db


with app.app_context():

    # Create any tables that do not already exist
    db.create_all()

    # Check the existing columns in the booking table
    inspector = inspect(db.engine)

    booking_columns = [
        column["name"]
        for column in inspector.get_columns("booking")
    ]

    # Add attendance_status only if it does not already exist
    if "attendance_status" not in booking_columns:

        db.session.execute(
            text(
                "ALTER TABLE booking "
                "ADD COLUMN attendance_status "
                "VARCHAR(20) DEFAULT 'Pending'"
            )
        )

        db.session.commit()

        print("attendance_status column added successfully.")

    else:

        print("attendance_status column already exists.")

    print("Database tables updated successfully.")