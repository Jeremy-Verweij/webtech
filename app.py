import io
from flask import make_response, render_template, request, redirect, url_for, session
import os

from sqlalchemy import func, and_, update
from sqlalchemy.orm import aliased
from setup import app, db, turbo
from models import *
from blueprints.auth import auth_blueprint
from utils.hash_password import hash_password
from utils.lang import get_lang, lang_names, default_lang
from utils.db_helpers import *

app.secret_key = os.urandom(24) 

app.register_blueprint(auth_blueprint)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if 'language' not in session:
        session['language'] = default_lang

    user_settings = db.session.query(Settings).where(Settings.UserId == session["user_id"]).one_or_none()

    if user_settings:
        session['dark_mode'] = user_settings.DarkMode
    else:
        session['dark_mode'] = False
        
    posts = get_posts()

    return render_template('index.html', user_name=session['user_name'], posts=posts, lang=get_lang(session['language']))

@app.route('/comments/<int:post_id>')
def comments(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if 'language' not in session:
        session['language'] = default_lang
        
    post = get_post(post_id)

    comments = get_comments(post_id)
    
    return render_template('comments.html', post=post, comments=comments, lang=get_lang(session['language']))

@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = db.session.query(User).where(User.id == user_id).one_or_none()
    posts = db.session.query(Post).where(Post.UserId == user_id).order_by(Post.creation_date.desc()).all()

    follower_count = db.session.query(following_table).filter_by(FollowedUserId=user_id).count()

    following_count = db.session.query(following_table).filter_by(UserId=user_id).count()

    following = db.session.query(User).join(following_table, User.id == following_table.c.FollowedUserId).filter(following_table.c.UserId == user_id).all()

    is_following = db.session.query(following_table).filter_by(UserId=session["user_id"], FollowedUserId=user_id).count() > 0

    if not user:
        return "User not found", 404
    
    if 'language' not in session:
        session['language'] = default_lang

    return render_template('profile.html', user=user, posts=posts, follower_count=follower_count, following_count=following_count, following=following, is_following=is_following, lang=get_lang(session['language']))

# Create Post
@app.route('/create_post', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    title = request.form.get('title')
    content = request.form.get('content')

    new_post = Post(session["user_id"], title, content)
    db.session.add(new_post)
    db.session.commit()
    
    turbo.push(turbo.prepend(\
        render_template("includes/post.html", user_name=session['user_name'], post=get_post(new_post.id), lang=get_lang(session['language'])),\
        "posts"))
    
    if turbo.can_stream():
        return turbo.stream(
            turbo.replace(render_template("includes/new_post.html", lang=get_lang(session['language'])), "new_post"),
        )
    else:
        return redirect(url_for('index'))

# Like Post
@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    existing_like = db.session.query(user_post_likes.c.PostId, user_post_likes.c.UserId) \
        .where(and_(user_post_likes.c.PostId == post_id, user_post_likes.c.UserId == session["user_id"])) \
        .one_or_none()
    post = db.session.query(Post).where(Post.id == post_id).one_or_none()
    user = db.session.query(User).where(User.id == session["user_id"]).one_or_none()

    if existing_like and post:
        post.likes.remove(user)
        db.session.add(post)
    else:
        post.likes.append(user)
        db.session.add(post)
    db.session.commit()

    if(post.ParentPostId == None):
        turbo.push(turbo.replace(\
            render_template("includes/post.html", user_name=session['user_name'], post=get_post(post_id), lang=get_lang(session['language'])),\
            f"post-{post_id}"))
    else:
        turbo.push(turbo.replace(\
            render_template("includes/comment.html", user_name=session['user_name'], comment=get_comment(post_id), lang=get_lang(session['language'])),\
            f"comment-{post_id}"))

    if turbo.can_stream():
        return turbo.stream(turbo.remove("unused_id"))
    else:
        return redirect(url_for('index'))

@app.route('/create_comment/<int:post_id>', methods=['POST'])
def create_comment(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    content = request.form.get('content')

    new_post = Post(session["user_id"], None, content, post_id)
    db.session.add(new_post)
    db.session.commit()

    return redirect(url_for('comments', post_id=post_id))

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db.session.execute(update(Post).where(and_(Post.id == post_id, session['user_id'] == Post.UserId)).values({Post.Title: None, Post.Content: None, Post.RepostId: None}))
    db.session.commit()
    
    turbo.push(turbo.replace(\
        render_template("includes/post.html", user_name=session['user_name'], post=get_post(post_id), lang=get_lang(session['language'])),\
        f"post-{post_id}"))

    if turbo.can_stream():
        return turbo.stream(turbo.remove("unused_id"))
    else:
        return redirect(url_for('index'))

# Follow/Unfollow User
@app.route('/follow/<int:user_id>', methods=['POST'])
def follow_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))


    existing_follow = db.session.query(following_table.c.UserId) \
        .where(and_(following_table.c.FollowedUserId == user_id, following_table.c.UserId == session["user_id"])) \
        .one_or_none()
    user_to_follow = db.session.query(User).where(User.id == user_id).one_or_none()
    user = db.session.query(User).where(User.id == session["user_id"]).one_or_none()

    if existing_follow and user_to_follow:
        user_to_follow.followers.remove(user)
        db.session.add(user)
    else:
        user_to_follow.followers.append(user)
        db.session.add(user)
    db.session.commit()

    # return ""
    return redirect('/profile/' + str(user_id))

# Repost
@app.route('/repost/<int:post_id>', methods=['POST'])
def repost(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    title = request.form.get('title')
    content = request.form.get('content')

    repost = Post(session["user_id"], title, content, None, post_id)
    db.session.add(repost)
    db.session.commit()

    turbo.push(turbo.prepend(\
        render_template("includes/post.html", user_name=session['user_name'], post=get_post(repost.id), lang=get_lang(session['language'])),\
        "posts"))

    if turbo.can_stream():
        return turbo.stream(turbo.replace( \
            render_template("includes/repost.html", lang=get_lang(session['language'])), \
            "repostModal"))
    else:
        return redirect(url_for('index'))


@app.route('/profile_picture/<int:user_id>')
def profile_picture(user_id):

    user = db.session.query(User).where(User.id == user_id).one_or_none()

    if user and user.ProfilePictureId != None:
        picture = db.session.query(ProfilePicture.id, ProfilePicture.imageData).where(ProfilePicture.id == user.ProfilePictureId).one_or_none()
        if picture.imageData:
            something = io.BytesIO(picture.imageData)
            response = make_response(something, 200)
            response.headers.set('Content-Type', 'image/jpeg')
            return response
    
    # Default profile picture
    return redirect(url_for('static', filename="default_profile.jpg"))  # Change this to your default image path


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    
    user = db.session.query(User).where(User.id == session["user_id"]).one_or_none()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        profile_picture = request.files.get('profile_picture')

        if username: 
            user.UserName = username

        if password:
            hashed_password = hash_password(password)
            user.passwordHash = hashed_password

        if profile_picture and profile_picture.filename != '':
            image_data = profile_picture.read()
            profile_pic = ProfilePicture(image_data)
            db.session.add(profile_pic)
            db.session.commit()
            db.session.query(User).where(User.id == session["user_id"]).update({User.ProfilePictureId: profile_pic.id})

        db.session.commit()
        
        session['user_name'] = username
        return redirect(url_for('edit_profile'))

    if 'language' not in session:
        session['language'] = default_lang

    return render_template('edit_profile.html', user=user, lang=get_lang(session['language']))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_settings = db.session.query(Settings).where(Settings.UserId == session["user_id"]).one_or_none()

    if user_settings is None:
        user_settings = Settings(session["user_id"])
        db.session.add(user_settings)
        db.session.commit()

    session['dark_mode'] = user_settings.DarkMode

    if request.method == 'POST':
        user_settings.Language = request.form['language']
        db.session.commit()
        return redirect(url_for('settings'))
    
    
    if 'language' not in session:
        session['language'] = default_lang

    return render_template('settings.html', language=user_settings.Language, user_settings=user_settings, lang=get_lang(session['language']), available_lang=lang_names)



@app.route('/toggle_dark_mode', methods=['POST'])
def toggle_dark_mode():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_settings = db.session.query(Settings).where(Settings.UserId == session["user_id"]).one_or_none()
    if not user_settings:
        user_settings = Settings(session["user_id"])
        db.session.add(user_settings)
        db.session.commit()

    user_settings.DarkMode = not user_settings.DarkMode
    db.session.commit()

    session['dark_mode'] = user_settings.DarkMode

    return redirect(url_for('settings')) 

@app.route('/change_language', methods=['POST'])
def change_language():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    language = request.form['language']

    res = db.session.query(Settings).where(Settings.UserId == session["user_id"]).update({Settings.Language: language})
    if res == 0:
        new_settings = Settings(session["user_id"], Language=language)
        db.session.add(new_settings)
    db.session.commit()
    session['language'] = language

    return redirect(url_for('index'))

def get_user_language():
    if 'language' in session:
        return session['language']

    if 'user_id' in session:
        lang = db.session.query(Settings.Language).where(Settings.UserId == session["user_id"]).one_or_none()
        if lang: session["language"] = lang
           
        return session['Language'] if lang else default_lang  # Default to English
    
    return default_lang  # Default for guests

if __name__ == '__main__':
    app.run(debug=True)
