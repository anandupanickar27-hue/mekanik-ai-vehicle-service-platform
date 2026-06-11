from flask import render_template, request
from app import app

from app.models import User
from app import db
from flask import redirect, url_for
from app.models import User, Vehicle
from app.models import Appointment, Vehicle
from app.ai_helper import categorize_issue
from app.gemini_helper import ask_gemini
from sqlalchemy import or_
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

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


from flask_login import login_user

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(
                url_for("dashboard")
            )

        return "Invalid email or password"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

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
        ai_recommendation = ask_gemini(
                            f"""
                            Vehicle Issue:
                            {issue_description}

                            Give:
                            - Possible cause
                            - Recommendation

                            Keep it short.
                            """
                            )
        category = categorize_issue(issue_description)

        appointment = Appointment(
            vehicle_id=vehicle_id,
            service_date=service_date,
            issue_description=issue_description,
            category=category,
            ai_recommendation=ai_recommendation
        )

        db.session.add(appointment)
        db.session.commit()

        return "Appointment booked successfully!"

    vehicles = Vehicle.query.all()

    return render_template(
        "book_appointment.html",
        vehicles=vehicles
    )

@app.route("/appointments")
def appointments():

    search = request.args.get("search", "")
    status = request.args.get("status", "")

    query = Appointment.query

    if search:
        query = query.filter(
            Appointment.issue_description.contains(search)
        )

    if status:
        query = query.filter_by(status=status)

    appointments = query.all()

    return render_template(
        "appointments.html",
        appointments=appointments,
        search=search,
        status=status
    )

@app.route("/appointment/<int:id>")
def appointment_details(id):

    appointment = Appointment.query.get(id)

    return render_template(
        "appointment_details.html",
        appointment=appointment
    )

@app.route("/update-status/<int:id>", methods=["GET", "POST"])
def update_status(id):

    appointment = Appointment.query.get(id)

    if request.method == "POST":

        appointment.status = request.form["status"]

        db.session.commit()

        return redirect(url_for("appointments"))

    return render_template(
        "update_status.html",
        appointment=appointment
    )

@app.route("/dashboard")
def dashboard():

    total_users = User.query.count()

    total_vehicles = Vehicle.query.count()

    total_appointments = Appointment.query.count()

    pending_appointments = Appointment.query.filter_by(
        status="Pending"
    ).count()

    completed_appointments = Appointment.query.filter_by(
        status="Completed"
    ).count()

    brake_count = Appointment.query.filter_by(
    category="Brake"
    ).count()

    battery_count = Appointment.query.filter_by(
    category="Battery"
    ).count()

    engine_count = Appointment.query.filter_by(
    category="Engine"
    ).count()

    tire_count = Appointment.query.filter_by(
    category="Tire"
    ).count()

    general_count = Appointment.query.filter_by(
    category="General"
    ).count()

    return render_template(
    "dashboard.html",
    total_users=total_users,
    total_vehicles=total_vehicles,
    total_appointments=total_appointments,
    pending_appointments=pending_appointments,
    completed_appointments=completed_appointments,

    brake_count=brake_count,
    battery_count=battery_count,
    engine_count=engine_count,
    tire_count=tire_count,
    general_count=general_count
)

@app.route("/ai-assistant", methods=["GET", "POST"])
def ai_assistant():

    response = None

    if request.method == "POST":

        issue = request.form["issue"]

        response = ask_gemini(
            f"""
            You are an automobile service expert.

            User issue:
            {issue}

            Give:
            1. Possible causes
            2. Recommended action
            3. Whether immediate service is needed

            Keep the response concise.
            """
        )

    return render_template(
        "ai_assistant.html",
        response=response
    )

