from flask import Blueprint, render_template, redirect, request, session, url_for
from sqlalchemy import and_, update
from setup import db, turbo
from models import *
from utils.db_helpers import get_comment, get_post
from utils.lang import get_lang
from utils.turbo_helper import push_except, session_id_to_turbo_id

post_blueprint = Blueprint("post", __name__, template_folder="templates")


# Create Post
@post_blueprint.route("/create_post", methods=["POST"])
def create_post():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    title = request.form.get("title")
    content = request.form.get("content")

    new_post = Post(session["user_id"], title, content)
    db.session.add(new_post)
    db.session.commit()

    turbo_id = None
    if session["user_id"] in session_id_to_turbo_id:
        turbo_id = session_id_to_turbo_id[session["user_id"]]

    push_except(turbo,
            turbo.prepend(
                render_template(
                    "includes/post_outer.html",
                    user_name=None,
                    post=get_post(new_post.id),
                    lang=get_lang(session["language"]),
                ),
                "posts"
            ),
            turbo_id
        )
    
    if turbo.can_stream():
        return turbo.stream([
            turbo.prepend(
                render_template(
                    "includes/post_outer.html",
                    user_name=session["user_name"],
                    post=get_post(new_post.id),
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
        ])
    else:
        return redirect(url_for("index"))

# Like Post
@post_blueprint.route("/like_post/<int:post_id>", methods=["POST"])
def like_post(post_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

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
def create_comment(post_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    content = request.form.get("content")

    new_post = Post(session["user_id"], None, content, post_id)
    db.session.add(new_post)
    db.session.commit()
    post = get_post(new_post.id)

    turbo.push(turbo.update(
        get_post(post_id).comments.__len__(),
        f"comments-{post_id}",
    ))
    
    turbo_id = None
    if session["user_id"] in session_id_to_turbo_id:
        turbo_id = session_id_to_turbo_id[session["user_id"]]

    push_except(turbo,
        turbo.prepend(
            render_template("includes/comment_outer.html",
            post=post,
            user_name=None,
            lang=get_lang(session["language"])),
            f".post-comments-{post_id}",
        multiple=True),
        turbo_id
    )
    
    if turbo.can_stream():
        return turbo.stream([
            turbo.replace(
                render_template("includes/new_comment.html",
                post={"id": post_id},
                lang=get_lang(session["language"])),
                f"post-comment-form-{post_id}"
            ),
                    turbo.prepend(
            render_template("includes/comment_outer.html",
                post=post,
                user_name=session["user_name"],
                lang=get_lang(session["language"])),
                f".post-comments-{post_id}",
            multiple=True),
        ])
    else:
        return redirect(url_for("index"))

@post_blueprint.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db.session.execute(
        update(Post)
        .where(and_(Post.id == post_id, session["user_id"] == Post.UserId))
        .values({Post.Title: None, Post.Content: None, Post.RepostId: None})
    )
    db.session.commit()

    post = db.session.query(Post).where(Post.id == post_id).one_or_none()
    
    delete_post_client = None
    
    if post.ParentPostId == None:
        delete_post_client = turbo.replace(
                render_template(
                    "includes/post.html",
                    user_name=session["user_name"],
                    post=get_post(post_id),
                    lang=get_lang(session["language"]),
                ),
                f"post-{post_id}",
            )
    else:
        delete_post_client = turbo.replace(
                render_template(
                    "includes/comment.html",
                    user_name=session["user_name"],
                    post=get_comment(post_id),
                    lang=get_lang(session["language"]),
                ),
                f"comment-{post_id}",
            )

    if turbo.can_stream():
        return turbo.stream(delete_post_client)
    else:
        return redirect(url_for("index"))

# Repost
@post_blueprint.route("/repost/<int:post_id>", methods=["POST"])
def repost(post_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    title = request.form.get("title")
    content = request.form.get("content")

    repost = Post(session["user_id"], title, content, None, post_id)
    db.session.add(repost)
    db.session.commit()

    turbo.push(
        turbo.prepend(
            render_template(
                "includes/post_outer.html",
                user_name=session["user_name"],
                post=get_post(repost.id),
                lang=get_lang(session["language"]),
            ),
            "posts",
        )
    )

    if turbo.can_stream():
        return turbo.stream(
            turbo.replace(
                render_template(
                    "includes/repost.html", lang=get_lang(session["language"])
                ),
                "repostModal",
            )
        )
    else:
        return redirect(url_for("index"))
