from typing import List
from sqlalchemy.orm import Mapped
from setup import db
from Post import Post

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    passwordHash: Mapped[str] = db.Column(
        db.Text,
    )
    EmailAdress: Mapped[str] = db.Column(db.String(50), unique=True)
    UserName: Mapped[str] = db.Column(db.String(50))
    Private: Mapped[bool] = db.Column(db.Boolean, default=False)
    ProfilePictureId: Mapped[int] = db.Column(db.Integer, nullable=True)

    posts: Mapped[List["Post"]] = db.relationship()

    def __init__(
        self, passwordHash, EmailAdress, UserName, Private=None, ProfilePictureId=None
    ):
        self.passwordHash = passwordHash
        self.EmailAdress = EmailAdress
        self.UserName = UserName
        self.Private = Private
        self.ProfilePictureId = ProfilePictureId

    def __repr__(self):
        return f"id: {self.id}, Username: {self.UserName}"