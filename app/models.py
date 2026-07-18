from app import db
from flask_login import UserMixin
from app import login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    password = db.Column(
    db.String(255),
    nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    phone = db.Column(
    db.String(15)
    )

    vehicles = db.relationship(
        "Vehicle",
        backref="owner",
        lazy=True
    )

    role = db.Column(
    db.String(20),
    nullable=False,
    default="customer"
    )

    mechanic_profile = db.relationship(
    "MechanicProfile",
    backref="user",
    uselist=False
    )

    reviews = db.relationship(
    "Review",
    foreign_keys="Review.mechanic_id",
    lazy=True
    )

    is_demo = db.Column(db.Boolean, default=False)

    


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)

    company = db.Column(db.String(100), nullable=False)

    model = db.Column(db.String(100), nullable=False)

    year = db.Column(db.Integer, nullable=False)

    registration_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    appointments = db.relationship(
    "Appointment",
    backref="vehicle",
    lazy=True
    )


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    issue_description = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Pending"
    )

    vehicle_id = db.Column(
        db.Integer,
        db.ForeignKey("vehicles.id"),
        nullable=False
    )

    mechanic_notes = db.Column(
    db.Text
    )

    category = db.Column(
    db.String(50)
    )   

    ai_recommendation = db.Column(db.Text) 

    mechanic_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id")
    )

    mechanic = db.relationship(
    "User",
    foreign_keys=[mechanic_id]
    )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class MechanicProfile(db.Model):

    __tablename__ = "mechanic_profiles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    specialization = db.Column(
        db.String(100),
        nullable=False
    )

    experience = db.Column(
        db.Integer,
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    available_slots = db.Column(
    db.Integer,
    default=5
    )

    rating = db.Column(
        db.Float,
        default=0
    )

    bio = db.Column(
        db.Text
    )

    review_count = db.Column(db.Integer, default=0)

    completed_jobs = db.Column(db.Integer, default=0)

class Review(db.Model):

    __tablename__ = "reviews"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    mechanic_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    comment = db.Column(
        db.Text
    )