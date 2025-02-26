import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
import os
import hashlib

from setup import *
from models import *

app.secret_key = os.urandom(24)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", user_name=session["user_name"])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = hash_password(request.form["password"])

        user = db.session.query(User).filter(User.EmailAdress == email).one_or_none()

        if user and user.passwordHash == password:
            session["user_id"] = user.id
            session["user_name"] = user.UserName

            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials.")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = hash_password(request.form["password"])

        new_user = User(password, email, username)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
