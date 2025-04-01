from sqlalchemy.orm import Mapped
from setup import db


class Settings(db.Model):
    __tablename__ = "settings"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserId: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )

    # Correct relationship definition
    User: Mapped["User"] = db.relationship("User", backref="settings")

    DarkMode: Mapped[bool] = db.Column(db.Boolean, default=False, nullable=False)
    Language: Mapped[str] = db.Column(db.String, default="en", nullable=False)

    def __init__(
        self, UserId, DarkMode=False, Language="en"
    ):  # Fixed darkMode -> DarkMode
        self.UserId = UserId
        self.DarkMode = DarkMode
        self.Language = Language

    def __repr__(self):
        return f"<Settings id={self.id}, user_id={self.UserId}, DarkMode={self.DarkMode}, Language={self.Language}>"