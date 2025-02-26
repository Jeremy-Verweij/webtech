from setup import db

following_table = db.Table(
    "following",
    db.Column("UserId", db.Integer, db.ForeignKey("users.id")),
    db.Column("FollowedUserId", db.Integer, db.ForeignKey("users.id")),
)
