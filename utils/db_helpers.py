from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from setup import db
from models import *


def get_post(post_id):
    stmt = (
        select(Post)
        .options(selectinload(Post.comments, recursion_depth=None))
        .where(Post.id == post_id)
    )
    res = db.session.execute(stmt).scalars().one_or_none()

    return res


def get_comment(comment_id):
    return (
        db.session.query(
            Post.id.label("CommentID"),
            Post.creation_date.label("Date"),
            Post.UserId.label("UserID"),
            func.count(user_post_likes.c.PostId).label("Likes"),
            User.UserName.label("UserName"),
            Post.Content.label("Content"),
        )
        .where(Post.id == comment_id)
        .join(User, User.id == Post.UserId)
        .outerjoin(user_post_likes, user_post_likes.c.PostId == Post.id)
        .group_by(Post.id)
        .order_by(Post.creation_date.desc())
        .one_or_none()
    )


def get_comments(post_id):
    return (
        db.session.query(
            Post.id.label("CommentID"),
            Post.creation_date.label("Date"),
            Post.UserId.label("UserID"),
            func.count(user_post_likes.c.PostId).label("Likes"),
            User.UserName.label("UserName"),
            Post.Content.label("Content"),
        )
        .where(Post.ParentPostId == post_id)
        .join(User, User.id == Post.UserId)
        .outerjoin(user_post_likes, user_post_likes.c.PostId == Post.id)
        .group_by(Post.id)
        .order_by(Post.creation_date.desc())
        .all()
    )


def get_posts():

    stmt = select(Post).options(selectinload(Post.comments, recursion_depth=None)).where(Post.ParentPostId == None)
    res = db.session.execute(stmt).scalars().all()

    return res
