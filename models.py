from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    contact = db.Column(
        db.String(15),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    is_approved = db.Column(
        db.Boolean,
        default=False
    )

    is_blacklisted = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    assigned_treks = db.relationship(
        "Trek",
        backref="assigned_staff",
        lazy=True
    )

    bookings = db.relationship(
        "Booking",
        backref="user",
        lazy=True
    )

    staff_profile = db.relationship(
        "StaffProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


class StaffProfile(db.Model):
    __tablename__ = "staff_profile"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        unique=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Trek(db.Model):
    __tablename__ = "trek"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    location = db.Column(
        db.String(100),
        nullable=False
    )

    difficulty = db.Column(
        db.String(30),
        nullable=False
    )

    duration = db.Column(
        db.Integer,
        nullable=False
    )

    maximum_slots = db.Column(
        db.Integer,
        nullable=False
    )

    available_slots = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    start_date = db.Column(
        db.Date,
        nullable=False
    )

    end_date = db.Column(
        db.Date,
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    bookings = db.relationship(
        "Booking",
        backref="trek",
        lazy=True
    )


class Booking(db.Model):
    __tablename__ = "booking"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("trek.id"),
        nullable=False
    )

    booking_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    status = db.Column(
        db.String(20),
        default="Booked"
    )

    payment_status = db.Column(
        db.String(20),
        default="Pending"
    )

    attendance_status = db.Column(
        db.String(20),
        default="Pending"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "trek_id",
            name="unique_booking"
        ),
    )