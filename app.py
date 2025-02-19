import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
import os

from setup import *
from models import *

app.secret_key = os.urandom(24)


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = db.session.query(User).filter(User.EmailAdress == email).one_or_none()

        if user and user.passwordHash == password:
            session["user_id"] = user.id
            session["user_name"] = user.UserName
            if user.settings:
                session["dark_mode"] = user.settings.DarkMode

            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Ongeldige inloggegevens.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user_name=session["user_name"])


if __name__ == "__main__":
    app.run(debug=True)
