import os
from flask import render_template, session
from setup import app
from blueprints import *
from utils.lang import get_lang
from utils.db_helpers import get_posts
from utils.jinja_uuid_gen import gen_uuid
from utils.turbo_helper import turbo_user_id_init
from flask_login import login_required

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
@login_required
def index():
    posts = get_posts()

    return render_template(
        "index.html",
        user_name=session["user_name"],
        posts=posts,
        lang=get_lang(session["language"]),
    )


if __name__ == "__main__":
    app.run(debug=True)
