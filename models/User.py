from typing import List
from sqlalchemy.orm import Mapped
from setup import db
from .Following import following_table
from .Like import user_post_likes

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    passwordHash: Mapped[str] = db.Column(
        db.Text,
    )
    EmailAdress: Mapped[str] = db.Column(db.String(50), unique=True)
    UserName: Mapped[str] = db.Column(db.String(50))
    Private: Mapped[bool] = db.Column(db.Boolean, default=False)

    ProfilePictureId: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("profile_pictures.id"), nullable=True
    )

    posts: Mapped[List["Post"]] = db.relationship("Post")

    following: Mapped[List["User"]] = db.relationship(
        "User",
        secondary=following_table,
        back_populates="followers",
        primaryjoin=(following_table.c.UserId == id),
        secondaryjoin=(following_table.c.FollowedUserId == id),
    )
    followers: Mapped[List["User"]] = db.relationship(
        "User",
        secondary=following_table,
        back_populates="following",
        primaryjoin=(following_table.c.FollowedUserId == id),
        secondaryjoin=(following_table.c.UserId == id),
    )

    liked_posts: Mapped[List["Post"]] = db.relationship(
        "Post", secondary=user_post_likes, back_populates="likes"
    )

    def __init__(
        self, passwordHash, EmailAdress, UserName, Private=None, ProfilePictureId=None
    ):
        self.passwordHash = passwordHash
        self.EmailAdress = EmailAdress
        self.UserName = UserName
        self.Private = Private
        self.ProfilePictureId = ProfilePictureId

    def __repr__(self):
        return f"<id: {self.id}, Username: {self.UserName}>"
