from typing import List
from sqlalchemy.orm import Mapped
from setup import db
from User import User

class Following(db.Model):
    __tablename__ = "followings"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)

    UserId: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    User: Mapped["User"] = db.relationship(foreign_keys=[UserId])

    FollowedUserId: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    FollowedUser: Mapped["User"] = db.relationship(foreign_keys=[FollowedUserId])