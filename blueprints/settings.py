from flask import Blueprint, redirect, render_template, request, session, url_for

from models import ProfilePicture, Settings, User
from setup import db
from utils.hash_password import hash_password
from utils.lang import get_lang, lang_names, default_lang


settings_blueprint = Blueprint("settings", __name__, template_folder="templates")

@settings_blueprint.route("/settings", methods=["GET"])
def settings():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_settings = (
        db.session.query(Settings)
        .where(Settings.UserId == session["user_id"])
        .one_or_none()
    )

    if user_settings is None:
        user_settings = Settings(session["user_id"])
        db.session.add(user_settings)
        db.session.commit()

    session["dark_mode"] = user_settings.DarkMode

    if "language" not in session:
        session["language"] = default_lang

    return render_template(
        "settings.html",
        language=user_settings.Language,
        user_settings=user_settings,
        lang=get_lang(session["language"]),
        available_lang=lang_names,
    )
    
@settings_blueprint.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = db.session.query(User).where(User.id == session["user_id"]).one_or_none()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        profile_picture = request.files.get("profile_picture")

        if username:
            user.UserName = username

        if password:
            hashed_password = hash_password(password)
            user.passwordHash = hashed_password

        if profile_picture and profile_picture.filename != "":
            image_data = profile_picture.read()
            profile_pic = ProfilePicture(image_data)
            db.session.add(profile_pic)
            db.session.commit()
            db.session.query(User).where(User.id == session["user_id"]).update(
                {User.ProfilePictureId: profile_pic.id}
            )

        db.session.commit()

        session["user_name"] = username
        return redirect(url_for("settings.edit_profile"))

    if "language" not in session:
        session["language"] = default_lang

    return render_template(
        "edit_profile.html", user=user, lang=get_lang(session["language"])
    )
    
@settings_blueprint.route("/toggle_dark_mode", methods=["POST"])
def toggle_dark_mode():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_settings = (
        db.session.query(Settings)
        .where(Settings.UserId == session["user_id"])
        .one_or_none()
    )
    if not user_settings:
        user_settings = Settings(session["user_id"])
        db.session.add(user_settings)
        db.session.commit()

    user_settings.DarkMode = not user_settings.DarkMode
    db.session.commit()

    session["dark_mode"] = user_settings.DarkMode

    return redirect(url_for("settings.settings"))

@settings_blueprint.route("/change_language", methods=["POST"])
def change_language():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    language = request.form["language"]

    res = (
        db.session.query(Settings)
        .where(Settings.UserId == session["user_id"])
        .update({Settings.Language: language})
    )
    if res == 0:
        new_settings = Settings(session["user_id"], Language=language)
        db.session.add(new_settings)
    db.session.commit()
    session["language"] = language

    return redirect(url_for("settings.settings"))