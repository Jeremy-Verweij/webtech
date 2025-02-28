from sqlalchemy.orm import Mapped
from setup import db

class Settings(db.Model):
    __tablename__ = "settings"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)

    UserId: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    User: Mapped["User"] = db.relationship(foreign_keys=[UserId])

    DarkMode: Mapped[bool] = db.Column(db.Boolean, default=False)
    Language: Mapped[str] = db.Column(db.String, default="EN")

    def __init__(self, UserId, darkMode=False, Language="EN"):
        self.UserId = UserId
        self.DarkMode = darkMode
        self.Language = Language

    def __repr__(self):
        return f"<id: {self.id}, user_id: {self.UserId}>"