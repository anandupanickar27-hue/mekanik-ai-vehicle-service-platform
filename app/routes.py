from flask import render_template, request
from app import app

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

@app.route("/db-test")
def db_test():
    db.session.execute(db.text("SELECT 1"))
    return "Database Connected!"
@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/vehicle/<int:id>")
def vehicle(id):
    return f"Vehicle ID: {id}"