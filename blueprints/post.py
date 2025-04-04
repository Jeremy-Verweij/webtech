from flask import Blueprint, render_template, redirect, request, session, url_for
from sqlalchemy import and_, update
from setup import db, turbo
from models import *
from utils.db_helpers import get_post
from utils.lang import get_lang
from utils.turbo_helper import push_except, session_id_to_turbo_id
from flask_login import login_required

post_blueprint = Blueprint("post", __name__, template_folder="templates")


# Create Post
@post_blueprint.route("/create_post", methods=["POST"])
@login_required
def create_post():

    title = request.form.get("title")
    content = request.form.get("content")

    new_post = Post(session["user_id"], title, content)
    db.session.add(new_post)
    db.session.commit()

    turbo_id = None
    if session["user_id"] in session_id_to_turbo_id:
        turbo_id = session_id_to_turbo_id[session["user_id"]]
    else:
        redirect(url_for("index"))

    push_except(
        turbo,
        turbo.prepend(
            render_template(
                "includes/post_outer.html",
                user_name=None,
                post=new_post,
                lang=get_lang(session["language"]),
            ),
            "posts",
        ),
        turbo_id,
    )

    if turbo.can_stream():
        return turbo.stream(
            [
                turbo.prepend(
                    render_template(
                        "includes/post_outer.html",
                        user_name=session["user_name"],
                        post=new_post,
                        lang=get_lang(session["language"]),
                    ),
                    "posts",
                ),
                turbo.replace(
                    render_template(
                        "includes/new_post.html", lang=get_lang(session["language"])
                    ),
                    "new_post",
                ),
            ]
        )
    else:
        return redirect(url_for("index"))


# Like Post
@post_blueprint.route("/like_post/<int:post_id>", methods=["POST"])
@login_required
def like_post(post_id):

    existing_like = (
        db.session.query(user_post_likes.c.PostId, user_post_likes.c.UserId)
        .where(
            and_(
                user_post_likes.c.PostId == post_id,
                user_post_likes.c.UserId == session["user_id"],
            )
        )
        .one_or_none()
    )
    post = db.session.query(Post).where(Post.id == post_id).one_or_none()
    user = db.session.query(User).where(User.id == session["user_id"]).one_or_none()

    if existing_like and post:
        post.likes.remove(user)
        db.session.add(post)
    else:
        post.likes.append(user)
        db.session.add(post)
    db.session.commit()

    turbo.push(
        turbo.update(
            post.likes.__len__(),
            f"likes-{post_id}",
        )
    )

    if turbo.can_stream():
        return turbo.stream(turbo.remove("unused_id"))
    else:
        return redirect(url_for("index"))


@post_blueprint.route("/create_comment/<int:post_id>", methods=["POST"])
@login_required
def create_comment(post_id):

    content = request.form.get("content")

    new_post = Post(session["user_id"], None, content, post_id)
    db.session.add(new_post)
    db.session.commit()

    turbo.push(
        turbo.update(
            get_post(post_id).comments.__len__(),
            f"comments-{post_id}",
        )
    )

    turbo_id = None
    if session["user_id"] in session_id_to_turbo_id:
        turbo_id = session_id_to_turbo_id[session["user_id"]]
    else:
        redirect(url_for("index"))

    push_except(
        turbo,
        turbo.append(
            render_template(
                "includes/comment_outer.html",
                post=new_post,
                user_name=None,
                lang=get_lang(session["language"]),
            ),
            f".post-comments-{post_id}",
            multiple=True,
        ),
        turbo_id,
    )

    if turbo.can_stream():
        return turbo.stream(
            [
                turbo.replace(
                    render_template(
                        "includes/new_comment.html",
                        post={"id": post_id},
                        lang=get_lang(session["language"]),
                    ),
                    f"post-comment-form-{post_id}",
                ),
                turbo.append(
                    render_template(
                        "includes/comment_outer.html",
                        post=new_post,
                        user_name=session["user_name"],
                        lang=get_lang(session["language"]),
                    ),
                    f".post-comments-{post_id}",
                    multiple=True,
                ),
            ]
        )
    else:
        return redirect(url_for("index"))


@post_blueprint.route("/delete_post/<int:post_id>", methods=["POST"])
@login_required
def delete_post(post_id):

    db.session.execute(
        update(Post)
        .where(and_(Post.id == post_id, session["user_id"] == Post.UserId))
        .values({Post.Title: None, Post.Content: None, Post.RepostId: None})
    )
    db.session.commit()

    turbo.push(
        [
            turbo.update("Deleted", f"title-{post_id}"),
            turbo.update("Deleted", f"content-{post_id}"),
        ]
    )

    if turbo.can_stream():
        return turbo.stream(turbo.remove("unused_id"))
    else:
        return redirect(url_for("index"))


# Repost
@post_blueprint.route("/repost/<int:post_id>", methods=["POST"])
@login_required
def repost(post_id):

    title = request.form.get("title")
    content = request.form.get("content")

    repost = Post(session["user_id"], title, content, None, post_id)
    db.session.add(repost)
    db.session.commit()

    turbo_id = None
    if session["user_id"] in session_id_to_turbo_id:
        turbo_id = session_id_to_turbo_id[session["user_id"]]
    else:
        redirect(url_for("index"))

    push_except(
        turbo,
        turbo.prepend(
            render_template(
                "includes/post_outer.html",
                user_name=None,
                post=get_post(repost.id),
                lang=get_lang(session["language"]),
            ),
            "posts",
        ),
        turbo_id,
    )

    return redirect(url_for("index"))
