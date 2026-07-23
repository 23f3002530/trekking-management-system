from sqlalchemy import inspect, text

from app import app
from models import db


with app.app_context():

    db.create_all()

    inspector = inspect(db.engine)

    booking_columns = [
        column["name"]
        for column in inspector.get_columns("booking")
    ]

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

    if "payment_status" not in booking_columns:

        db.session.execute(
            text(
                "ALTER TABLE booking "
                "ADD COLUMN payment_status "
                "VARCHAR(20) DEFAULT 'Pending'"
            )
        )

        db.session.commit()

        print("payment_status column added successfully.")

    else:

        print("payment_status column already exists.")

    print("Database tables updated successfully.")