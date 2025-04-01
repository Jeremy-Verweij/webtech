from flask import Blueprint, render_template, redirect, request, session, url_for
from forms.login import LoginForm
from forms.register import RegistrationForm
from setup import db
from models import *
from flask_login import login_user, login_required, logout_user

auth_blueprint = Blueprint(
    "auth", __name__, template_folder="templates", url_prefix="/auth"
)


# Login
@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if request.method == "POST" and form.validate():
        email = form.email.data

        user = db.session.query(User).filter(User.EmailAdress == email).one_or_none()

        if user and user.check_password(form.password.data):
            login_user(user)
            set_session(user)

            return redirect(url_for("index"))
        else:
            form.email.errors.append("Invalid credentials.")

    return render_template("login.html", form=form)


# Register
@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)

    if request.method == "POST" and form.validate():
        email = form.email.data
        username = form.username.data
        password = form.password.data

        try:
            new_user = User(password, email, username)
            db.session.add(new_user)
            db.session.commit()
        except:
            form.email.errors.append("Email already in use.")
            return render_template("register.html", form=form)

        user = db.session.query(User).filter(User.EmailAdress == email).one_or_none()
        login_user(user)
        set_session(user)

        return redirect(url_for("index"))

    return render_template("register.html", form=form)


# Logout
@auth_blueprint.route("/logout")
@login_required
def logout():
    session.clear()
    session.modified = True
    logout_user()
    return redirect(url_for("auth.login"))


def set_session(user: User):
    user_settings = (
        db.session.query(Settings).where(Settings.UserId == user.id).one_or_none()
    )

    session["user_id"] = user.id
    session["user_name"] = user.UserName

    if user_settings:
        session["dark_mode"] = user_settings.DarkMode
        session["language"] = user_settings.Language
    else:
        session["dark_mode"] = False
        session["language"] = "en"

    session.modified = True
