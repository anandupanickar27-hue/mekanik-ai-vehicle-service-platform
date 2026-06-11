from flask import render_template, request
from app import app

from app.models import User
from app import db
from flask import redirect, url_for
from app.models import User, Vehicle
from app.models import Appointment, Vehicle


@app.route("/test-form", methods=["GET", "POST"])
def test_form():

    if request.method == "POST":

        name = request.form["name"]

        return f"Hello {name}"

    return render_template("test_form.html")

@app.route("/")
def home():
    return render_template(
        "index.html",
        platform_name="Mekanik",
        owner="Anandu"
    )


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/vehicle/<int:id>")
def vehicle(id):
    return f"Vehicle ID: {id}"

@app.route("/add-user", methods=["GET", "POST"])
def add_user():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]

        user = User(
            name=name,
            email=email
        )

        db.session.add(user)
        db.session.commit()

        return "User saved successfully!"

    return render_template("add_user.html")

@app.route("/users")
def users():

    users = User.query.all()

    return render_template(
        "users.html",
        users=users
    )

@app.route("/delete-user/<int:id>")
def delete_user(id):

    user = User.query.get(id)

    db.session.delete(user)

    db.session.commit()

    return redirect(url_for("users"))

@app.route("/edit-user/<int:id>", methods=["GET", "POST"])
def edit_user(id):

    user = User.query.get(id)

    if request.method == "POST":

        user.name = request.form["name"]
        user.email = request.form["email"]

        db.session.commit()

        return redirect(url_for("users"))

    return render_template(
        "edit_user.html",
        user=user
    )

@app.route("/add-vehicle", methods=["GET", "POST"])
def add_vehicle():

    if request.method == "POST":
        user_id = request.form["user_id"]
        company = request.form["company"]
        model = request.form["model"]
        year = request.form["year"]
        registration_number = request.form["registration_number"]

        vehicle = Vehicle(
                        company=company,
                        model=model,
                        year=year,
                        registration_number=registration_number,
                        user_id=user_id
                            )

        db.session.add(vehicle)
        db.session.commit()
        return "Vehicle saved successfully!"

    users = User.query.all()

    return render_template(
        "add_vehicle.html",
        users=users
        )


@app.route("/vehicles")
def vehicles():
    vehicles=Vehicle.query.all()

    return render_template("vehicles.html", vehicles=vehicles )


@app.route("/book-appointment", methods=["GET", "POST"])
def book_appointment():

    if request.method == "POST":

        vehicle_id = request.form["vehicle_id"]
        service_date = request.form["service_date"]
        issue_description = request.form["issue_description"]

        appointment = Appointment(
            vehicle_id=vehicle_id,
            service_date=service_date,
            issue_description=issue_description
        )

        db.session.add(appointment)
        db.session.commit()

        return "Appointment booked successfully!"

    vehicles = Vehicle.query.all()

    return render_template(
        "book_appointment.html",
        vehicles=vehicles
    )