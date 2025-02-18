from typing import List
from sqlalchemy.orm import Mapped
from setup import db

class ProfilePicture(db.Model):
    __tablename__ = "profile_pictures"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)

    imageData: Mapped[bytes] = db.Column(db.LargeBinary)

