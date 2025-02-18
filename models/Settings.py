from typing import List
from sqlalchemy.orm import Mapped
from setup import db
from User import User

class Settings(db.Model):
    __tablename__ = "settings"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)

    UserId: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    User: Mapped["User"] = db.relationship(foreign_keys=[UserId])

    DarkMode: Mapped[bool] = db.Column(db.Boolean, default=False)
