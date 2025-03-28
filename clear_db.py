from sqlalchemy import delete
from sqlalchemy.orm import aliased
from setup import app, db
from models import *

with app.app_context():
    db.session.execute(delete(Post))
    db.session.commit()
    
    db.session.execute(delete(user_post_likes))
    db.session.commit()
    
    db.session.execute(delete(ProfilePicture))
    db.session.commit()
    
    db.session.execute(delete(following_table))
    db.session.commit()
    
    db.session.execute(delete(Settings))
    db.session.commit()
    
    db.session.execute(delete(User))
    db.session.commit()
    