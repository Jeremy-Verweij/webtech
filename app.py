import os
from flask import render_template, redirect, url_for, session
from setup import app, db
from models import *
from blueprints import *
from utils.lang import get_lang, default_lang
from utils.db_helpers import *
from utils.jinja_uuid_gen import gen_uuid
from utils.turbo_helper import turbo_user_id_init

app.secret_key = os.urandom(24)

app.add_template_filter(gen_uuid)

app.register_blueprint(auth_blueprint)
app.register_blueprint(post_blueprint)
app.register_blueprint(user_profile_blueprint)
app.register_blueprint(settings_blueprint)

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

if __name__ == "__main__":
    app.run(debug=True)
