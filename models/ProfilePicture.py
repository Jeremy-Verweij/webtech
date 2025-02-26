from sqlalchemy.orm import Mapped
from setup import db

class ProfilePicture(db.Model):
    __tablename__ = "profile_pictures"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)

    imageData: Mapped[bytes] = db.Column(db.LargeBinary)

    def __init__(self, image):
        self.imageData = image

    def __repr__(self):
        return f"<id: {self.id}>"