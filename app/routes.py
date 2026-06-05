from flask import render_template
from app import app

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