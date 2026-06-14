from flask import render_template, request
from app import app

from app.models import User, Vehicle, Appointment, MechanicProfile
from flask_login import current_user
from app import db
from flask import redirect, url_for
from app.ai_helper import categorize_issue
from app.gemini_helper import ask_gemini
from sqlalchemy import or_
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from flask_login import login_required
from flask_login import logout_user

from functools import wraps
from flask_login import current_user

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if current_user.role != "admin":
            return "Access Denied"

        return f(*args, **kwargs)

    return decorated_function

@app.route("/test-form", methods=["GET", "POST"])
def test_form():

    if request.method == "POST":

        name = request.form["name"]

        return f"Hello {name}"

    return render_template("test_form.html")

@app.route("/")
def home():

    if current_user.is_authenticated:

        if current_user.role == "mechanic":
            return redirect(url_for("mechanic_dashboard"))

        return redirect(url_for("dashboard"))

    return render_template("index.html")


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

            if user.role == "mechanic":

                if not user.mechanic_profile:
                    return redirect(
                    url_for("complete_mechanic_profile")
                     )

                return redirect(
                url_for("mechanic_dashboard")
                )

            return redirect(url_for("dashboard"))

        return "Invalid email or password"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/vehicle/<int:id>")
@login_required
def vehicle(id):
    return f"Vehicle ID: {id}"

@app.route("/add-user", methods=["GET", "POST"])
@login_required
@admin_required
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
@login_required
@admin_required
def users():

    users = User.query.all()

    return render_template(
        "users.html",
        users=users
    )

@app.route("/delete-user/<int:id>")
@login_required
@admin_required
def delete_user(id):

    user = User.query.get(id)

    db.session.delete(user)

    db.session.commit()

    return redirect(url_for("users"))

@app.route("/edit-user/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
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
@login_required
def add_vehicle():

    if request.method == "POST":
        user_id = current_user.id
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
        return redirect(
            url_for("vehicles")
        )

    return render_template(
        "add_vehicle.html",
        )


@app.route("/vehicles")
@login_required
def vehicles():
    vehicles = Vehicle.query.filter_by(
                user_id=current_user.id
                ).all()

    return render_template("vehicles.html", vehicles=vehicles )


@app.route("/book-appointment", methods=["GET", "POST"])
@login_required
def book_appointment():

    if request.method == "POST":

        vehicle_id = request.form["vehicle_id"]
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

        recommended_mechanics = User.query.join(
            MechanicProfile
        ).filter(
            User.role == "mechanic",
            MechanicProfile.specialization == category
        ).all()

        return render_template(
            "recommended_mechanics.html",
            mechanics=recommended_mechanics,
            vehicle_id=vehicle_id,
            issue_description=issue_description,
            category=category,
            ai_recommendation=ai_recommendation
        )

    vehicles = Vehicle.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "book_appointment.html",
        vehicles=vehicles
    )

@app.route("/appointments")
@login_required
def appointments():

    search = request.args.get("search", "")
    status = request.args.get("status", "")

    query = Appointment.query.join(Vehicle).filter(
        Vehicle.user_id == current_user.id
    )

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
@login_required
def appointment_details(id):

    appointment = Appointment.query.get(id)

    if appointment.vehicle.user_id != current_user.id:
        return "Access Denied"

    return render_template(
        "appointment_details.html",
        appointment=appointment
    )

@app.route("/update-status/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
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
@login_required
def dashboard():

    my_vehicles = Vehicle.query.filter_by(
        user_id=current_user.id
    ).count()

    my_appointments = Appointment.query.join(Vehicle).filter(
        Vehicle.user_id == current_user.id
    ).count()

    pending_appointments = Appointment.query.join(Vehicle).filter(
        Vehicle.user_id == current_user.id,
        Appointment.status == "Pending"
    ).count()

    completed_appointments = Appointment.query.join(Vehicle).filter(
        Vehicle.user_id == current_user.id,
        Appointment.status == "Completed"
    ).count()

    return render_template(
        "dashboard.html",
        my_vehicles=my_vehicles,
        my_appointments=my_appointments,
        pending_appointments=pending_appointments,
        completed_appointments=completed_appointments
    )
@app.route("/ai-assistant", methods=["GET", "POST"])
@login_required
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

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))

@app.route("/profile")
@login_required
def profile():

    return render_template(
        "profile.html",
        user=current_user
    )

@app.route("/mechanic-dashboard")
@login_required
def mechanic_dashboard():

    return render_template(
        "mechanic_dashboard.html"
    )

@app.route("/complete-mechanic-profile", methods=["GET", "POST"])
@login_required
def complete_mechanic_profile():

    if request.method == "POST":

        specialization = request.form["specialization"]
        experience = request.form["experience"]
        phone = request.form["phone"]
        bio = request.form["bio"]

        profile = MechanicProfile(
            user_id=current_user.id,
            specialization=specialization,
            experience=experience,
            phone=phone,
            bio=bio
        )

        db.session.add(profile)
        db.session.commit()

        return redirect(url_for("mechanic_dashboard"))

    return render_template(
        "complete_mechanic_profile.html"
    )

@app.route("/edit-mechanic-profile", methods=["GET", "POST"])
@login_required
def edit_mechanic_profile():

    if current_user.role != "mechanic":
        return "Access Denied"

    profile = current_user.mechanic_profile

    if request.method == "POST":

        profile.specialization = request.form["specialization"]
        profile.experience = request.form["experience"]
        profile.phone = request.form["phone"]
        profile.bio = request.form["bio"]

        db.session.commit()

        return redirect(url_for("profile"))

    return render_template(
        "edit_mechanic_profile.html",
        profile=profile
    )

@app.route("/mechanics")
@login_required
def mechanics():

    mechanics = User.query.filter_by(
        role="mechanic"
    ).all()

    return render_template(
        "mechanics.html",
        mechanics=mechanics
    )

@app.route("/my-jobs")
@login_required
def my_jobs():

    jobs = Appointment.query.filter_by(
        mechanic_id=current_user.id
    ).all()

    return render_template(
        "my_jobs.html",
        jobs=jobs
    )

@app.route("/update-job-status/<int:id>", methods=["GET", "POST"])
@login_required
def update_job_status(id):

    job = Appointment.query.get(id)

    if job.mechanic_id != current_user.id:
        return "Access Denied"

    if request.method == "POST":

        job.status = request.form["status"]

        db.session.commit()

        return redirect(url_for("my_jobs"))

    return render_template(
        "update_job_status.html",
        job=job
    )

@app.route("/mechanic/<int:id>")
@login_required
def mechanic_details(id):

    mechanic = User.query.get(id)

    if mechanic.role != "mechanic":
        return "Mechanic not found"

    return render_template(
        "mechanic_details.html",
        mechanic=mechanic
    )

@app.route("/review-mechanic/<int:id>", methods=["GET", "POST"])
@login_required
def review_mechanic(id):

    if current_user.role != "customer":
        return "Access Denied"

    mechanic = User.query.get(id)

    completed_job = Appointment.query.filter_by(
    mechanic_id=mechanic.id,
    status="Completed"
    ).join(Vehicle).filter(
    Vehicle.user_id == current_user.id
    ).first()

    if not completed_job:
        return "You can review only after a completed service"

    if request.method == "POST":

        rating = int(request.form["rating"])
        comment = request.form["comment"]

        existing_review = Review.query.filter_by(
        mechanic_id=mechanic.id,
        customer_id=current_user.id
        ).first()

        if existing_review:
            return "You have already reviewed this mechanic"

        review = Review(
        mechanic_id=mechanic.id,
        customer_id=current_user.id,
        rating=rating,
        comment=comment
        )

        db.session.add(review)
        db.session.commit()


        reviews = Review.query.filter_by(
        mechanic_id=mechanic.id
        ).all()

        total_rating = sum(
        review.rating for review in reviews
        )

        average_rating = total_rating / len(reviews)

        mechanic.mechanic_profile.rating = round(
        average_rating,
        1
        )

        db.session.commit()

        return redirect(
        url_for("mechanic_details", id=id)
    )

    return render_template(
        "review_mechanic.html",
        mechanic=mechanic
    )

@app.route("/confirm-appointment", methods=["POST"])
@login_required
def confirm_appointment():

    appointment = Appointment(
        vehicle_id=request.form["vehicle_id"],
        mechanic_id=request.form["mechanic_id"],
        issue_description=request.form["issue_description"],
        category=request.form["category"],
        ai_recommendation=request.form["ai_recommendation"]
    )

    db.session.add(appointment)
    db.session.commit()

    return redirect(
        url_for("appointments")
    )