from setup import db

user_post_likes = db.Table(
    "likes",
    db.Column("UserId", db.Integer, db.ForeignKey("users.id")),
    db.Column("PostId", db.Integer, db.ForeignKey("posts.id")),
)
