from sqlalchemy import func, and_, update
from sqlalchemy.orm import aliased
from setup import app, db
from models import *

def get_post(post_id):
    Repost = aliased(Post)
    RepostUser = aliased(User)
    
    return db.session.query(\
            Post.id.label("PostID"), \
            Post.UserId.label("UserID"), \
            Post.Title.label("Title"), \
            Post.Content.label("Content"), \
            Post.creation_date.label("Date"), \
            User.UserName.label("UserName"), \
            func.count(user_post_likes.c.PostId).label("Likes"), \
            Repost.Title.label('RepostTitle'), \
            Repost.Content.label('RepostContent'), \
            Repost.UserId.label('RepostUserId'), \
            Repost.creation_date.label('RepostDate'), \
            RepostUser.UserName.label('RepostUserName')) \
        .outerjoin(user_post_likes, user_post_likes.c.PostId == Post.id) \
        .outerjoin(Repost, Repost.id == Post.RepostId)\
        .outerjoin(RepostUser, RepostUser.id == Repost.UserId) \
        .join(User, User.id == Post.UserId) \
        .where(Post.id == post_id) \
        .group_by(Post.id, Repost.id) \
        .one_or_none()
        
def get_comment(comment_id):
    return db.session.query(\
        Post.id.label("CommentID"), \
        Post.creation_date.label("Date"), \
        Post.UserId.label("UserID"), \
        func.count(user_post_likes.c.PostId).label("Likes"), \
        User.UserName.label("UserName"), \
        Post.Content.label("Content")) \
    .where(Post.id == comment_id) \
    .join(User, User.id == Post.UserId) \
    .outerjoin(user_post_likes, user_post_likes.c.PostId == Post.id) \
    .group_by(Post.id) \
    .order_by(Post.creation_date.desc()) \
    .one_or_none()
    
def get_comments(post_id):
    return db.session.query(\
        Post.id.label("CommentID"), \
        Post.creation_date.label("Date"), \
        Post.UserId.label("UserID"), \
        func.count(user_post_likes.c.PostId).label("Likes"), \
        User.UserName.label("UserName"), \
        Post.Content.label("Content")) \
    .where(Post.ParentPostId == post_id) \
    .join(User, User.id == Post.UserId) \
    .outerjoin(user_post_likes, user_post_likes.c.PostId == Post.id) \
    .group_by(Post.id) \
    .order_by(Post.creation_date.desc()) \
    .all()

def get_posts():
    Repost = aliased(Post)
    RepostUser = aliased(User)
    
    return db.session.query(\
            Post.id.label("PostID"), \
            Post.UserId.label("UserID"), \
            Post.Title.label("Title"), \
            Post.Content.label("Content"), \
            Post.creation_date.label("Date"), \
            User.UserName.label("UserName"), \
            func.count(user_post_likes.c.PostId).label("Likes"), \
            Repost.Title.label('RepostTitle'), \
            Repost.Content.label('RepostContent'), \
            Repost.UserId.label('RepostUserId'), \
            Repost.creation_date.label('RepostDate'), \
            RepostUser.UserName.label('RepostUserName')) \
        .outerjoin(user_post_likes, user_post_likes.c.PostId == Post.id) \
        .outerjoin(Repost, Repost.id == Post.RepostId)\
        .outerjoin(RepostUser, RepostUser.id == Repost.UserId) \
        .join(User, User.id == Post.UserId) \
        .order_by(Post.creation_date.desc()) \
        .where(Post.ParentPostId == None) \
        .group_by(Post.id, Repost.id) \
        .all()