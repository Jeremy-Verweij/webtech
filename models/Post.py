from datetime import datetime
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from setup import db
from .Like import user_post_likes


class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = db.mapped_column(db.Integer, primary_key=True, autoincrement=True)
    Title: Mapped[str] = db.Column(db.String(50))
    Content: Mapped[str] = db.Column(db.Text)
    creation_date: Mapped[datetime] = db.Column(db.DateTime, default=datetime.now)

    UserId: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    User: Mapped["User"] = db.relationship(
        back_populates="posts", foreign_keys=[UserId]
    )

    ParentPostId: Mapped[int] = db.Column(db.Integer, db.ForeignKey("posts.id"))
    parent_post = db.relationship(
        "Post", back_populates="comments", remote_side=[id], foreign_keys=[ParentPostId]
    )
    comments: Mapped[List["Post"]] = db.relationship(
        "Post",
        back_populates="parent_post",
        foreign_keys=[ParentPostId],
    )

    RepostId: Mapped[int] = db.mapped_column(db.Integer, db.ForeignKey("posts.id"))
    Repost = db.relationship("Post", remote_side=[id], foreign_keys=[RepostId])

    likes: Mapped[List["User"]] = db.relationship(
        "User", secondary=user_post_likes, back_populates="liked_posts"
    )

    def __init__(self, UserId, Title, Content, ParentPostId=None, RepostId=None):
        self.UserId = UserId
        self.ParentPostId = ParentPostId
        self.RepostId = RepostId
        self.Title = Title
        self.Content = Content

    def __repr__(self):
        return f"<id: {self.id}, title: {self.Title}, content: {self.Content}, userId: {self.UserId}>"