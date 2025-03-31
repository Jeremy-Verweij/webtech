from io import BytesIO
from flask import Blueprint, make_response, redirect, url_for, session, render_template
from sqlalchemy import and_
from utils.db_helpers import get_posts_from_user
from utils.lang import get_lang, lang_names, default_lang
from setup import db
from models import *
from flask_login import login_required

user_profile_blueprint = Blueprint(
    "user_profile", __name__, template_folder="templates"
)


@user_profile_blueprint.route("/profile_picture/<int:user_id>")
@login_required
def profile_picture(user_id):

    user = db.session.query(User).where(User.id == user_id).one_or_none()

    if user and user.ProfilePictureId != None:
        picture = (
            db.session.query(ProfilePicture.id, ProfilePicture.imageData)
            .where(ProfilePicture.id == user.ProfilePictureId)
            .one_or_none()
        )
        if picture.imageData:
            something = BytesIO(picture.imageData)
            response = make_response(something, 200)
            response.headers.set("Content-Type", "image/jpeg")
            return response

    # Default profile picture
    return redirect(
        url_for("static", filename="default_profile.jpg")
    )  # Change this to your default image path


@user_profile_blueprint.route("/profile/<int:user_id>")
@login_required
def profile(user_id):

    user = db.session.query(User).where(User.id == user_id).one_or_none()
    posts = get_posts_from_user(user_id) 

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
        session.modified = True

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


@user_profile_blueprint.route("/user_name/<user_name>")
@login_required
def user_name(user_name):
    user = db.session.query(User).where(User.UserName == str(user_name)).one_or_none()

    print(str(user_name))

    if user == None:
        return redirect(url_for("index"))

    return redirect(url_for("user_profile.profile", user_id=user.id))


# Follow/Unfollow User
@user_profile_blueprint.route("/follow/<int:user_id>", methods=["POST"])
@login_required
def follow_user(user_id):

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

    return redirect(url_for("user_profile.profile", user_id=user_id))
