import io
from flask import make_response, render_template, request, redirect, url_for, session
import os

from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField
from wtforms.validators import DataRequired

from sqlalchemy import and_
from setup import app, db
from models import *
from blueprints import auth_blueprint, post_blueprint
from utils.hash_password import hash_password
from utils.lang import get_lang, lang_names, default_lang
from utils.db_helpers import *
from utils.jinja_uuid_gen import gen_uuid
from utils.turbo_helper import turbo_user_id_init

app.secret_key = os.urandom(24)

app.add_template_filter(gen_uuid)

app.register_blueprint(auth_blueprint)
app.register_blueprint(post_blueprint)

turbo_user_id_init()

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if "language" not in session:
        session["language"] = default_lang
        
    user_settings = (
        db.session.query(Settings)
        .where(Settings.UserId == session["user_id"])
        .one_or_none()
    )

    if user_settings:
        session["dark_mode"] = user_settings.DarkMode
    else:
        session["dark_mode"] = False

    posts = get_posts()

    return render_template(
        "index.html",
        user_name=session["user_name"],
        posts=posts,
        lang=get_lang(session["language"]),
    )

@app.route("/user_name/<user_name>")
def user_name(user_name):
    user = db.session.query(User).where(User.UserName == str(user_name)).one_or_none()
    
    if user == None:
        return redirect(url_for("index"))
    
    return redirect(url_for("profile", user_id = user.id))

@app.route("/comments/<int:post_id>")
def comments(post_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if "language" not in session:
        session["language"] = default_lang

    post = get_post(post_id)

    comments = get_comments(post_id)

    return render_template(
        "comments.html",
        post=post,
        comments=comments,
        lang=get_lang(session["language"]),
    )


@app.route("/profile/<int:user_id>")
def profile(user_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = db.session.query(User).where(User.id == user_id).one_or_none()
    posts = (
        db.session.query(Post)
        .where(Post.UserId == user_id)
        .order_by(Post.creation_date.desc())
        .all()
    )

    follower_count = (
        db.session.query(following_table).filter_by(FollowedUserId=user_id).count()
    )

    following_count = (
        db.session.query(following_table).filter_by(UserId=user_id).count()
    )

    following = (
        db.session.query(User)
        .join(following_table, User.id == following_table.c.FollowedUserId)
        .filter(following_table.c.UserId == user_id)
        .all()
    )

    is_following = (
        db.session.query(following_table)
        .filter_by(UserId=session["user_id"], FollowedUserId=user_id)
        .count()
        > 0
    )

    if not user:
        return "User not found", 404

    if "language" not in session:
        session["language"] = default_lang

    return render_template(
        "profile.html",
        user=user,
        posts=posts,
        follower_count=follower_count,
        following_count=following_count,
        following=following,
        is_following=is_following,
        lang=get_lang(session["language"]),
    )


# Follow/Unfollow User
@app.route("/follow/<int:user_id>", methods=["POST"])
def follow_user(user_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    existing_follow = (
        db.session.query(following_table.c.UserId)
        .where(
            and_(
                following_table.c.FollowedUserId == user_id,
                following_table.c.UserId == session["user_id"],
            )
        )
        .one_or_none()
    )
    user_to_follow = db.session.query(User).where(User.id == user_id).one_or_none()
    user = db.session.query(User).where(User.id == session["user_id"]).one_or_none()

    if existing_follow and user_to_follow:
        user_to_follow.followers.remove(user)
        db.session.add(user)
    else:
        user_to_follow.followers.append(user)
        db.session.add(user)
    db.session.commit()

    # return ""
    return redirect("/profile/" + str(user_id))


@app.route("/profile_picture/<int:user_id>")
def profile_picture(user_id):

    user = db.session.query(User).where(User.id == user_id).one_or_none()

    if user and user.ProfilePictureId != None:
        picture = (
            db.session.query(ProfilePicture.id, ProfilePicture.imageData)
            .where(ProfilePicture.id == user.ProfilePictureId)
            .one_or_none()
        )
        if picture.imageData:
            something = io.BytesIO(picture.imageData)
            response = make_response(something, 200)
            response.headers.set("Content-Type", "image/jpeg")
            return response

    # Default profile picture
    return redirect(
        url_for("static", filename="default_profile.jpg")
    )  # Change this to your default image path


@app.route("/edit_profile", methods=["GET", "POST"])
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
        return redirect(url_for("edit_profile"))

    if "language" not in session:
        session["language"] = default_lang

    return render_template(
        "edit_profile.html", user=user, lang=get_lang(session["language"])
    )

class SettingsForm(FlaskForm):
    language = SelectField('Language', coerce=str, choices=[], validators=[DataRequired()])
    dark_mode = BooleanField('Enable Dark Mode')

@app.route("/settings", methods=["GET", "POST"])
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

    form = SettingsForm()

    form.language.choices = [(lang, name) for lang, name in lang_names.items()]
    
    form.language.data = user_settings.Language
    form.dark_mode.data = user_settings.DarkMode

    if form.validate_on_submit():
        if form.language.data != user_settings.Language:
            user_settings.Language = form.language.data
            db.session.commit()
            session["language"] = form.language.data
            return redirect(url_for("settings"))

    if "language" not in session:
        session["language"] = default_lang

    return render_template(
        "settings.html",
        form=form,
        lang=get_lang(session["language"]),
    )



@app.route("/toggle_dark_mode", methods=["POST"])
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

    return redirect(url_for("settings"))

@app.route("/change_language", methods=["POST"])
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

    return redirect(url_for("index"))


def get_user_language():
    if "language" in session:
        return session["language"]

    if "user_id" in session:
        lang = (
            db.session.query(Settings.Language)
            .where(Settings.UserId == session["user_id"])
            .one_or_none()
        )
        if lang:
            session["language"] = lang

        return session["Language"] if lang else default_lang  # Default to English

    return default_lang  # Default for guests


if __name__ == "__main__":
    app.run(debug=True)
