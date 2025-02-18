from typing import List
from sqlalchemy.orm import Mapped
from setup import db
from User import User
from Post import Post

class Like(db.Model):
    __tablename__ = "likes"

    UserId: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )
    User: Mapped["User"] = db.relationship(foreign_keys=[UserId])

    PostId: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("posts.id"), primary_key=True, nullable=False
    )
    Post: Mapped["Post"] = db.relationship(foreign_keys=[PostId])
