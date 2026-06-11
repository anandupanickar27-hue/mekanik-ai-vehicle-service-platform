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

    vehicles = db.relationship(
        "Vehicle",
        backref="owner",
        lazy=True
    )


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

class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    service_date = db.Column(
        db.String(20),
        nullable=False
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

    category = db.Column(
    db.String(50)
    )   

    ai_recommendation = db.Column(db.Text) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))