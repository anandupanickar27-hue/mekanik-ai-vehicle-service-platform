from functools import wraps

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from sqlalchemy import or_

from email_validator import (
    validate_email,
    EmailNotValidError
)

from app import app, db

from app.models import (
    User,
    Vehicle,
    Appointment,
    MechanicProfile,
    Review
)
import json
from app.ai_helper import categorize_issue
from app.gemini_helper import ask_gemini
from demo_reset import reset_demo_data

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if current_user.role != "admin":
            return "Access Denied"

        return f(*args, **kwargs)

    return decorated_function

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

        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()

        if not email or not password:
            flash("Email and password are required.")
            return render_template("login.html")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            if user.role == "admin":
                return redirect(
                    url_for("admin_dashboard")
                )

            elif user.role == "mechanic":

                if not user.mechanic_profile:
                    return redirect(
                        url_for("complete_mechanic_profile")
                    )

                return redirect(
                    url_for("mechanic_dashboard")
                )

            return redirect(
                url_for("dashboard")
            )

        flash("Invalid email or password.", "danger")
        return render_template("login.html")

    return render_template("login.html")

@app.route("/demo/customer")
def demo_customer_login():

    reset_demo_data()

    user = User.query.filter_by(
        email="demo.customer@mekanik.com"
    ).first()

    login_user(user)

    flash("Logged in as Demo Customer", "success")

    return redirect(url_for("dashboard"))

@app.route("/demo/mechanic")
def demo_mechanic_login():

    reset_demo_data()

    user = User.query.filter_by(
        email="demo.mechanic@mekanik.com"
    ).first()

    login_user(user)

    flash("Logged in as Demo Mechanic", "success")

    return redirect(url_for("mechanic_dashboard"))

import re
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()
        role = request.form["role"]

        # Validate name
        if len(name) < 3:
            flash("Name must be at least 3 characters long.")
            return render_template("register.html")

        if not re.fullmatch(r"[A-Za-z ]+", name):
            flash("Name can contain only letters and spaces.")
            return render_template("register.html")

        # Validate email
        try:
            email = validate_email(email).normalized

        except EmailNotValidError:
            flash("Invalid email address.")
            return render_template("register.html")

        # Check if email already exists
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
           flash("Email already registered.", "danger")
           return render_template("register.html")
        # Validate password
        if len(password) < 8:
            flash("Password must be at least 8 characters long.")
            return render_template("register.html")

        if not re.search(r"[A-Z]", password):
            flash("Password must contain at least one uppercase letter.")
            return render_template("register.html")

        if not re.search(r"[a-z]", password):
            flash("Password must contain at least one lowercase letter.")
            return render_template("register.html")

        if not re.search(r"\d", password):
            flash("Password must contain at least one number.")
            return render_template("register.html")

        # Create user
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

@app.route("/admin-dashboard")
@login_required
@admin_required
def admin_dashboard():

    total_users = User.query.count()

    total_customers = User.query.filter_by(
        role="customer"
    ).count()

    total_mechanics = User.query.filter_by(
        role="mechanic"
    ).count()

    total_vehicles = Vehicle.query.count()

    total_appointments = Appointment.query.count()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_customers=total_customers,
        total_mechanics=total_mechanics,
        total_vehicles=total_vehicles,
        total_appointments=total_appointments
    )

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
        query = query.filter(
            Appointment.status == status
        )

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

    in_progress_appointments = Appointment.query.join(Vehicle).filter(
    Vehicle.user_id == current_user.id,
    Appointment.status == "In Progress"
    ).count()

    return render_template(
    "dashboard.html",
    my_vehicles=my_vehicles,
    my_appointments=my_appointments,
    pending_appointments=pending_appointments,
    in_progress_appointments=in_progress_appointments,
    completed_appointments=completed_appointments,
)

@app.route("/about")
def about():

    return render_template("about.html")

@app.route("/ai-assistant", methods=["GET", "POST"])
@login_required
def ai_assistant():

    response = None
    mechanics = []
    category = None

    vehicles = Vehicle.query.filter_by(
        user_id=current_user.id
    ).all()

    selected_vehicle = None

    if request.method == "POST":

        vehicle_id = request.form["vehicle_id"]
        issue = request.form["issue"]

        selected_vehicle = Vehicle.query.get_or_404(vehicle_id)

        prompt = f"""
You are Mekanik AI, an expert automobile diagnostic assistant.

Vehicle Details:
Company: {selected_vehicle.company}
Model: {selected_vehicle.model}
Year: {selected_vehicle.year}

Customer Complaint:
{issue}

IMPORTANT INSTRUCTIONS:

1. First determine whether the customer's complaint is related to automobiles or vehicles.

2. Vehicle-related topics include:
- Cars
- Bikes
- Trucks
- Vehicle servicing
- Repairs
- Maintenance
- Engine
- Brakes
- Battery
- Tires
- Suspension
- AC
- Electrical systems
- Spare parts
- Diagnostics
- Fuel system
- Transmission
- Automotive safety

3. If the question is NOT related to vehicles or automobiles, DO NOT answer it.

Instead return ONLY this JSON:

{{
    "invalid_query": true,
    "message": "⚠️ Mekanik AI only answers vehicle-related questions. Please ask about vehicle maintenance, repairs, servicing, diagnostics, or automotive issues."
}}

4. If the question IS vehicle-related, return ONLY this JSON format:

{{
    "invalid_query": false,
    "possible_cause": "...",
    "severity": "Low/Medium/High",
    "safe_to_drive": "Yes/No/Only short distances",
    "recommended_action": "...",
    "estimated_repair": "₹2,500 - ₹4,000"
}}

Use realistic repair estimates in Indian Rupees (₹).

Typical repair cost guidelines:

- Minor service: ₹500–₹2,000
- Oil change: ₹1,000–₹3,000
- Brake pad replacement: ₹2,000–₹8,000
- Battery replacement: ₹4,000–₹10,000
- Tire alignment/balancing: ₹500–₹2,000
- AC service/gas refill: ₹2,000–₹6,000
- Suspension repair: ₹3,000–₹15,000
- Clutch replacement: ₹8,000–₹20,000
- Engine diagnostics: ₹1,000–₹3,000
- Major engine repair: ₹20,000–₹80,000
- Transmission repair: ₹15,000–₹60,000

Only suggest prices within these realistic ranges unless the issue clearly indicates catastrophic engine or transmission failure.

Rules:
- Return ONLY valid JSON.
- Do not use markdown.
- Do not use ```json.
- Do not include explanations outside the JSON.
- Never answer non-vehicle questions.
"""

        raw_response = ask_gemini(prompt)

        raw_response = raw_response.replace("```json", "")
        raw_response = raw_response.replace("```", "")
        raw_response = raw_response.strip()

        try:
            response = json.loads(raw_response)

            # Check if the AI rejected a non-vehicle query
            if response.get("invalid_query"):
                return render_template(
                "ai_assistant.html",
                vehicles=vehicles,
                selected_vehicle=selected_vehicle,
                error="⚠️ This is not a valid vehicle-related issue. Please ask about vehicle maintenance, repairs, servicing, diagnostics, or automotive problems.",
                response=None,
                mechanics=[],
                invalid_query=True
            )

        except Exception:
            response = {
                "possible_cause": raw_response,
                "severity": "Unknown",
                "safe_to_drive": "Unknown",
                "recommended_action": "Consult a qualified mechanic.",
                "estimated_repair": "Not Available"
            }
        CATEGORY_MAPPING = {
            "Engine": "Engine & Transmission",
            "Transmission": "Engine & Transmission",
            "Brake": "Brakes & Suspension",
            "Brakes": "Brakes & Suspension",
            "Suspension": "Brakes & Suspension",
            "Electrical": "Electrical Systems",
            "Battery": "Battery & Charging",
            "Charging": "Battery & Charging",
            "AC": "Air Conditioning",
            "Air Conditioning": "Air Conditioning",
            "Tyre": "Tires & Wheels",
            "Tire": "Tires & Wheels",
            "Wheel": "Tires & Wheels",
            "Diagnostic": "Diagnostics",
            "Diagnostics": "Diagnostics",
            "Service": "General Service",
        }
        category = categorize_issue(issue)

        category = CATEGORY_MAPPING.get(category, category)

        mechanics = (
            User.query
            .join(MechanicProfile)
            .filter(
                User.role == "mechanic",
                or_(
                    MechanicProfile.specialization == category,
                    User.is_demo == True
                )
            )
            .all()
                )

        mechanics.sort(
            key=lambda m: (
                not m.is_demo,
                -m.mechanic_profile.rating
            )
        )

    return render_template(
    "ai_assistant.html",
    vehicles=vehicles,
    selected_vehicle=selected_vehicle,
    response=response,
    mechanics=mechanics,
    invalid_query=False
)

@app.route("/logout")
@login_required
def logout():

    if current_user.is_authenticated and current_user.is_demo:
        reset_demo_data()

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

    appointments = (
        Appointment.query
        .filter_by(mechanic_id=current_user.id)
        .join(Vehicle)
        .all()
    )

    pending_count = Appointment.query.filter_by(
        mechanic_id=current_user.id,
        status="Pending"
    ).count()

    in_progress_count = Appointment.query.filter_by(
        mechanic_id=current_user.id,
        status="In Progress"
    ).count()

    completed_count = Appointment.query.filter_by(
        mechanic_id=current_user.id,
        status="Completed"
    ).count()

    return render_template(
        "mechanic_dashboard.html",
        appointments=appointments,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        completed_count=completed_count
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

        current_user.name = request.form["name"]
        current_user.email = request.form["email"]
        current_user.phone = request.form["user_phone"]

        profile.specialization = request.form["specialization"]
        profile.experience = request.form["experience"]
        profile.phone = request.form["mechanic_phone"]
        profile.bio = request.form["bio"]

        db.session.commit()

        return redirect(url_for("profile"))

    return render_template(
        "edit_mechanic_profile.html",
        user=current_user,
        profile=profile
    )

@app.route("/mechanics")
@login_required
def mechanics():

    search = request.args.get("search", "").strip()

    query = User.query.filter_by(
        role="mechanic"
    ).join(
        MechanicProfile
    )

    if search:

        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                MechanicProfile.specialization.ilike(f"%{search}%")
            )
        )

    mechanics = query.all()

    return render_template(
        "mechanics.html",
        mechanics=mechanics,
        search=search
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

    vehicle_id = request.form["vehicle_id"]
    mechanic_id = request.form["mechanic_id"]
    issue = request.form["issue_description"]
    ai_recommendation = request.form["ai_recommendation"]

    vehicle = Vehicle.query.get_or_404(vehicle_id)

    # Prevent booking someone else's vehicle
    if vehicle.user_id != current_user.id:
        flash("Invalid vehicle selected.", "danger")
        return redirect(url_for("ai_assistant"))

    mechanic = User.query.filter_by(
        id=mechanic_id,
        role="mechanic"
    ).first_or_404()

    category = categorize_issue(issue)

    appointment = Appointment(
        vehicle_id=vehicle.id,
        mechanic_id=mechanic.id,
        issue_description=issue,
        status="Pending",
        category=category,
        ai_recommendation=ai_recommendation
    )

    db.session.add(appointment)
    db.session.commit()

    flash(
        f"Appointment booked successfully with {mechanic.name}.",
        "success"
    )

    return redirect(url_for("appointments"))
@app.route("/update-job-status/<int:id>", methods=["GET", "POST"])
@login_required
def update_job_status(id):

    job = Appointment.query.get(id)

    if job.mechanic_id != current_user.id:
        return "Access Denied"

    if request.method == "POST":

        old_status = job.status
        new_status = request.form["status"]

        job.status = new_status
        job.mechanic_notes = request.form[
        "mechanic_notes"
        ]

        if (
            old_status != "Completed"
            and new_status == "Completed"
        ):

            mechanic = User.query.get(
                job.mechanic_id
            )

            mechanic.mechanic_profile.available_slots += 1

        db.session.commit()

        return redirect(
            url_for("my_jobs")
        )

    return render_template(
        "update_job_status.html",
        job=job
    )

@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():

    if request.method == "POST":

        current_user.name = request.form["name"]
        current_user.email = request.form["email"]
        current_user.phone = request.form["phone"]

        db.session.commit()

        return redirect(
            url_for("profile")
        )

    return render_template(
        "edit_profile.html",
        user=current_user
    )

@app.route("/book-with-mechanic/<int:id>", methods=["GET", "POST"])
@login_required
def book_with_mechanic(id):

    mechanic = User.query.get_or_404(id)

    if request.method == "POST":

        appointment = Appointment(
            vehicle_id=request.form["vehicle_id"],
            mechanic_id=mechanic.id,
            issue_description=request.form["issue_description"],
            category="General Service",
            ai_recommendation="Booked directly from mechanic page",
            status="Pending"
        )

        db.session.add(appointment)

        mechanic.mechanic_profile.available_slots -= 1

        db.session.commit()

        return redirect(
            url_for("appointments")
        )

    vehicles = Vehicle.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "book_with_mechanic.html",
        mechanic=mechanic,
        vehicles=vehicles
    )

@app.route("/cancel-appointment/<int:id>")
@login_required
def cancel_appointment(id):

    appointment = Appointment.query.get_or_404(id)

    if appointment.vehicle.user_id != current_user.id:
        return "Access Denied"

    if appointment.status == "Completed":
        return "Completed appointments cannot be cancelled"

    mechanic = User.query.get(
        appointment.mechanic_id
    )

    if mechanic:
        mechanic.mechanic_profile.available_slots += 1

    db.session.delete(appointment)
    db.session.commit()

    return redirect(
        url_for("appointments")
    )

@app.route("/delete-vehicle/<int:id>")
@login_required
def delete_vehicle(id):

    vehicle = Vehicle.query.get_or_404(id)

    if vehicle.user_id != current_user.id:
        return "Access Denied"

    db.session.delete(vehicle)
    db.session.commit()

    return redirect(
        url_for("vehicles")
    )