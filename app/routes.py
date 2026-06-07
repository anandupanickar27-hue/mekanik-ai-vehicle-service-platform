from flask import render_template, request
from app import app

from app.models import User
from app import db


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