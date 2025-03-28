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

def get_posts():

    stmt = select(Post).options(selectinload(Post.comments, recursion_depth=None)).where(Post.ParentPostId == None)
    res = db.session.execute(stmt).scalars().all()

    return res
