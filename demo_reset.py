from app import app, db
from werkzeug.security import generate_password_hash
from app.models import (
    User,
    MechanicProfile,
    Vehicle,
    Appointment
)

from collections import defaultdict
import random

MECHANICS = [
    # Name, Email, Specialization, Experience, Rating, Reviews, Completed Jobs

    # Engine & Transmission
    ("Rahul Sharma", "rahul.engine@mekanik.com", "Engine & Transmission", 8, 4.8, 186, 412),
    ("Arjun Menon", "arjun.engine@mekanik.com", "Engine & Transmission", 6, 4.7, 142, 305),
    ("Vivek Nair", "vivek.engine@mekanik.com", "Engine & Transmission", 10, 4.9, 267, 598),

    # Electrical Systems
    ("Sandeep Kumar", "sandeep.electrical@mekanik.com", "Electrical Systems", 7, 4.6, 119, 274),
    ("Akash Thomas", "akash.electrical@mekanik.com", "Electrical Systems", 9, 4.8, 201, 463),
    ("Nikhil Das", "nikhil.electrical@mekanik.com", "Electrical Systems", 5, 4.7, 97, 211),

    # Brakes & Suspension
    ("Ajay Singh", "ajay.brakes@mekanik.com", "Brakes & Suspension", 11, 4.9, 295, 645),
    ("Rohan George", "rohan.brakes@mekanik.com", "Brakes & Suspension", 8, 4.8, 184, 401),
    ("Manoj Pillai", "manoj.brakes@mekanik.com", "Brakes & Suspension", 6, 4.6, 123, 282),

    # Tires & Wheels
    ("Arun Raj", "arun.tires@mekanik.com", "Tires & Wheels", 7, 4.7, 136, 318),
    ("Kiran Joseph", "kiran.tires@mekanik.com", "Tires & Wheels", 9, 4.8, 214, 491),

    # Air Conditioning
    ("Faisal Khan", "faisal.ac@mekanik.com", "Air Conditioning", 10, 4.9, 281, 612),
    ("Ashwin Babu", "ashwin.ac@mekanik.com", "Air Conditioning", 6, 4.7, 118, 267),

    # Battery & Charging
    ("Rohit Verma", "rohit.battery@mekanik.com", "Battery & Charging", 8, 4.8, 176, 389),
    ("Santhosh S", "santhosh.battery@mekanik.com", "Battery & Charging", 5, 4.6, 88, 196),

    # General Service
    ("Deepak Paul", "deepak.general@mekanik.com", "General Service", 12, 4.7, 326, 721),
    ("Vinod Kumar", "vinod.general@mekanik.com", "General Service", 9, 4.8, 238, 544),
    ("Sreehari", "sreehari.general@mekanik.com", "General Service", 11, 4.9, 302, 683),

    # Diagnostics
    ("Praveen R", "praveen.diag@mekanik.com", "Diagnostics", 10, 4.8, 227, 518),
    ("Joel Mathew", "joel.diag@mekanik.com", "Diagnostics", 7, 4.7, 151, 347),
]

def seed_mechanics():

    for (
        name,
        email,
        specialization,
        experience,
        rating,
        review_count,
        completed_jobs
    ) in MECHANICS:

        user = User.query.filter_by(email=email).first()

        if not user:

            user = User(
                name=name,
                email=email,
                password=generate_password_hash("Demo@123"),
                role="mechanic",
                phone="9999999999",
                is_demo=False
            )

            db.session.add(user)
            db.session.commit()

            print(f"✅ Created mechanic: {name}")

        else:

            user.name = name
            user.role = "mechanic"
            user.phone = "9999999999"

        profile = MechanicProfile.query.filter_by(
            user_id=user.id
        ).first()

        if not profile:

            profile = MechanicProfile(
                user_id=user.id
            )

            db.session.add(profile)

        profile.specialization = specialization
        profile.experience = experience
        profile.phone = "9999999999"
        profile.available_slots = 5
        profile.rating = rating
        profile.review_count = review_count
        profile.completed_jobs = completed_jobs

        profile.bio = (
            f"{specialization} specialist with "
            f"{experience} years of professional experience. "
            f"Successfully completed over {completed_jobs} repairs and "
            f"earned {review_count} customer reviews. "
            "Experienced in diagnostics, repairs, preventive maintenance, "
            "and delivering reliable customer service."
        )

    db.session.commit()

    print("✅ All mechanics seeded successfully.")

def reset_demo_data():

    with app.app_context():

        # ==========================================
        # DEMO CUSTOMER
        # ==========================================

        demo_customer = User.query.filter_by(
            email="demo.customer@mekanik.com"
        ).first()

        if not demo_customer:

            demo_customer = User(
                name="Demo Customer",
                email="demo.customer@mekanik.com",
                password=generate_password_hash("Demo@123"),
                role="customer",
                phone="9XXXXXXXXX",
                is_demo=True
            )

            db.session.add(demo_customer)
            db.session.commit()

            print("✅ Demo Customer created")

        else:

            demo_customer.name = "Demo Customer"
            demo_customer.phone = "9XXXXXXXXX"
            demo_customer.password = generate_password_hash("Demo@123")
            demo_customer.role = "customer"
            demo_customer.is_demo = True

            print("♻️ Demo Customer reset")

        # ==========================================
        # DEMO MECHANIC
        # ==========================================

        demo_mechanic = User.query.filter_by(
            email="demo.mechanic@mekanik.com"
        ).first()

        if not demo_mechanic:

            demo_mechanic = User(
                name="Demo Mechanic",
                email="demo.mechanic@mekanik.com",
                password=generate_password_hash("Demo@123"),
                role="mechanic",
                phone="9876543211",
                is_demo=True
            )

            db.session.add(demo_mechanic)
            db.session.commit()

            print("✅ Demo Mechanic created")

        else:

            demo_mechanic.name = "Demo Mechanic"
            demo_mechanic.phone = "9876543211"
            demo_mechanic.password = generate_password_hash("Demo@123")
            demo_mechanic.role = "mechanic"
            demo_mechanic.is_demo = True

            print("♻️ Demo Mechanic reset")

        # ==========================================
        # DEMO MECHANIC PROFILE
        # ==========================================

        mechanic_profile = MechanicProfile.query.filter_by(
            user_id=demo_mechanic.id
        ).first()

        if not mechanic_profile:

            mechanic_profile = MechanicProfile(
                user_id=demo_mechanic.id
            )

            db.session.add(mechanic_profile)

        mechanic_profile.specialization = "Engine & Transmission"
        mechanic_profile.experience = 8
        mechanic_profile.phone = "9XXXXXXXXX"
        mechanic_profile.available_slots = 5
        mechanic_profile.rating = 4.8
        mechanic_profile.bio = (
            "ASE-certified mechanic with 8 years of experience in "
            "engine diagnostics, transmission repair, preventive "
            "maintenance, and electrical troubleshooting. "
            "Committed to honest service and customer satisfaction."
        )

        print("♻️ Demo Mechanic Profile reset")

        # ==========================================
        # REMOVE EXTRA VEHICLES
        # ==========================================

        Vehicle.query.filter(
            Vehicle.user_id == demo_customer.id,
            Vehicle.registration_number.notin_(
                [
                    "KL07AB1234",
                    "KL07CD5678"
                ]
            )
        ).delete(synchronize_session=False)

        # ==========================================
        # DEMO VEHICLE 1
        # ==========================================

        vehicle = Vehicle.query.filter_by(
            registration_number="KL07AB1234"
        ).first()

        if not vehicle:

            vehicle = Vehicle(
                company="Honda",
                model="City",
                year=2022,
                registration_number="KL07AB1234",
                user_id=demo_customer.id
            )

            db.session.add(vehicle)

        else:

            vehicle.company = "Honda"
            vehicle.model = "City"
            vehicle.year = 2022
            vehicle.user_id = demo_customer.id

        print("♻️ Honda City reset")

        # ==========================================
        # DEMO VEHICLE 2
        # ==========================================

        vehicle = Vehicle.query.filter_by(
            registration_number="KL07CD5678"
        ).first()

        if not vehicle:

            vehicle = Vehicle(
                company="Royal Enfield",
                model="Classic 350",
                year=2023,
                registration_number="KL07CD5678",
                user_id=demo_customer.id
            )

            db.session.add(vehicle)

        else:

            vehicle.company = "Royal Enfield"
            vehicle.model = "Classic 350"
            vehicle.year = 2023
            vehicle.user_id = demo_customer.id

        print("♻️ Royal Enfield Classic 350 reset")

        # ==========================================
        # SEED ADDITIONAL MECHANICS
        # ==========================================

        seed_mechanics()
        db.session.commit()

        seed_demo_appointments(demo_customer, demo_mechanic)

        db.session.commit()

def seed_demo_appointments(demo_customer, demo_mechanic):

    # Remove old demo appointments
    Appointment.query.filter(
        Appointment.vehicle.has(user_id=demo_customer.id)
    ).delete(synchronize_session=False)

    db.session.commit()

    vehicles = Vehicle.query.filter_by(user_id=demo_customer.id).all()

    if len(vehicles) < 2:
        return

    car = vehicles[0]
    bike = vehicles[1]

    mechanics = defaultdict(list)

    for mechanic in User.query.filter_by(role="mechanic").all():

        if mechanic.mechanic_profile:

            mechanics[
                mechanic.mechanic_profile.specialization
            ].append(mechanic)

    def pick(spec):

        return random.choice(mechanics[spec])

    appointments = [

    # =======================
    # COMPLETED APPOINTMENTS
    # =======================

    {
        "vehicle": car,
        "mechanic": pick("Brakes & Suspension"),
        "status": "Completed",
        "category": "Brakes & Suspension",
        "issue": "Brake pedal feels soft while stopping.",
        "notes": "Front brake pads replaced, brake fluid topped up, road test completed.",
        "ai": "Possible worn brake pads. Severity: Medium. Safe to drive for short distance only."
    },

    {
        "vehicle": car,
        "mechanic": pick("Battery & Charging"),
        "status": "Completed",
        "category": "Battery & Charging",
        "issue": "Battery drains overnight.",
        "notes": "Battery replaced and charging system tested successfully.",
        "ai": "Battery health poor. Replacement recommended."
    },

    {
        "vehicle": car,
        "mechanic": pick("Tires & Wheels"),
        "status": "Completed",
        "category": "Tires & Wheels",
        "issue": "Vehicle pulls to the left while driving.",
        "notes": "Wheel alignment and balancing completed.",
        "ai": "Wheel alignment required."
    },

    {
        "vehicle": bike,
        "mechanic": pick("General Service"),
        "status": "Completed",
        "category": "General Service",
        "issue": "Scheduled periodic maintenance.",
        "notes": "Engine oil changed, air filter cleaned, chain lubricated.",
        "ai": "Routine maintenance recommended."
    },

    {
        "vehicle": bike,
        "mechanic": pick("Engine & Transmission"),
        "status": "Completed",
        "category": "Engine & Transmission",
        "issue": "Engine vibration at high RPM.",
        "notes": "Spark plug replaced and throttle body cleaned.",
        "ai": "Spark plug wear detected."
    },

    {
        "vehicle": bike,
        "mechanic": pick("Diagnostics"),
        "status": "Completed",
        "category": "Diagnostics",
        "issue": "Check engine light appeared intermittently.",
        "notes": "Diagnostic scan completed. Fault code cleared after sensor replacement.",
        "ai": "Faulty oxygen sensor detected."
    },

    # =======================
    # ACTIVE APPOINTMENTS
    # =======================

    {
        "vehicle": car,
        "mechanic": demo_mechanic,
        "status": "In Progress",
        "category": "Engine & Transmission",
        "issue": "Knocking sound while accelerating.",
        "notes": "",
        "ai": "Possible timing chain wear or piston knock. Detailed inspection in progress."
    },

    {
        "vehicle": bike,
        "mechanic": demo_mechanic,
        "status": "Pending",
        "category": "Diagnostics",
        "issue": "Engine warning light remains ON after starting.",
        "notes": "",
        "ai": "Electronic fault suspected. Full diagnostic scan recommended."
    }

]

    for data in appointments:

        db.session.add(

            Appointment(

                vehicle_id=data["vehicle"].id,

                mechanic_id=data["mechanic"].id,

                issue_description=data["issue"],

                status=data["status"],

                category=data["category"],

                mechanic_notes=data["notes"],

                ai_recommendation=data["ai"]

            )

        )

    db.session.commit()

    print("✅ Demo appointments seeded.")

if __name__ == "__main__":

    reset_demo_data()

    print("\n🎉 Demo data reset successfully!")