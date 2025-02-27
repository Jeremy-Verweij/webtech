import sqlite3
from flask import render_template, request, redirect, url_for, session, flash
import os
import hashlib

from sqlalchemy import func
from setup import app, db
from models import *

app.secret_key = os.urandom(24) 

db_path = 'database/db.sqlite'

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    posts = db.session.query(Post.id.label("PostID"), Post.Title.label("Title"), Post.Content.label("Content"), User.UserName.label("UserName"), func.count(user_post_likes.c.PostId).label("Likes")) \
        .outerjoin(user_post_likes, user_post_likes.c.PostId == Post.id) \
        .join(User, User.id == Post.UserId) \
        .group_by(Post.id).all()

    return render_template('index.html', user_name=session['user_name'], posts=posts)

# Create Post
@app.route('/create_post', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form.get('title')
    content = request.form.get('content')

    new_post = Post(session["user_id"], title, content)
    db.session.add(new_post)
    db.session.commit()

    return redirect(url_for('index'))

# Like Post
@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    existing_like = db.session.query(user_post_likes.c.PostId) \
        .where(user_post_likes.c.PostId == post_id and user_post_likes.c.UserId == session["user_id"]) \
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
    
    return redirect(url_for('index'))

# Follow/Unfollow User
@app.route('/follow/<int:user_id>', methods=['POST'])
def follow_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))


    existing_follow = db.session.query(following_table.c.UserId) \
        .where(following_table.c.FollowedUserId == user_id and following_table.c.UserId == session["user_id"]) \
        .one_or_none()
    user_to_follow = db.session.query(User).where(User.id == user_id).one_or_none()
    user = db.session.query(User).where(User.id == session["user_id"]).one_or_none()

    if existing_follow and user_to_follow:
        user_to_follow.followers.remove(user)
        db.session.add(user)
    else:
        user_to_follow.likes.append(user)
        db.session.add(user)
    db.session.commit()

    return redirect(url_for('index'))

# Repost
@app.route('/repost/<int:post_id>', methods=['POST'])
def repost(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    repost = Post(session["user_id"], None, None, None, post_id)
    db.session.add(repost)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/profile_picture/<int:user_id>')
def profile_picture(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT ProfilePicture FROM Users WHERE UUID = ?', (user_id,)).fetchone()
    conn.close()

    if user and user['ProfilePicture']:
        conn = get_db_connection()
        picture = conn.execute('SELECT ImageData FROM ProfilePictures WHERE PictureID = ?', (user['ProfilePicture'],)).fetchone()
        conn.close()
        if picture:
            return (picture['ImageData'], 200, {'Content-Type': 'image/jpeg'})  # or 'image/png'
    
    # Default profile picture
    return redirect("https://via.placeholder.com/40")  # Change this to your default image path


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Users WHERE UUID = ?', (session['user_id'],)).fetchone()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        profile_picture = request.files.get('profile_picture')

        conn.execute('UPDATE Users SET UserName = ? WHERE UUID = ?', (username, session['user_id']))
        
        if password:
            hashed_password = hash_password(password)
            conn.execute('UPDATE Users SET PasswordHash = ? WHERE UUID = ?', (hashed_password, session['user_id']))

        if profile_picture and profile_picture.filename != '':
            image_data = profile_picture.read()
            conn.execute('INSERT INTO ProfilePictures (ImageData) VALUES (?)', (image_data,))
            picture_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            conn.execute('UPDATE Users SET ProfilePicture = ? WHERE UUID = ?', (picture_id, session['user_id']))

        conn.commit()
        conn.close()
        
        session['user_name'] = username
        return redirect(url_for('index'))

    return render_template('edit_profile.html', user=user)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user_settings = conn.execute("SELECT Language FROM Settings WHERE UserID = ?", (session['user_id'],)).fetchone()

    if request.method == 'POST':
        language = request.form['language']
        
        if user_settings:
            conn.execute("UPDATE Settings SET Language = ? WHERE UserID = ?", (language, session['user_id']))
        else:
            conn.execute("INSERT INTO Settings (UserID, Language) VALUES (?, ?)", (session['user_id'], language))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('settings.html', language=user_settings['Language'] if user_settings else 'en')

@app.route('/change_language', methods=['POST'])
def change_language():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    language = request.form['language']

    conn = get_db_connection()
    conn.execute("UPDATE Settings SET Language = ? WHERE UserID = ?", 
                 (language, session['user_id']))
    conn.commit()
    conn.close()
    
    # Store the selected language in session
    session['language'] = language

    return redirect(url_for('index'))

def get_user_language():
    if 'language' in session:
        return session['language']

    if 'user_id' in session:
        conn = get_db_connection()
        lang = conn.execute("SELECT Language FROM Settings WHERE UserID = ?", 
                            (session['user_id'],)).fetchone()
        conn.close()
        return lang['Language'] if lang else 'EN'  # Default to English
    
    return 'EN'  # Default for guests

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])
        
        user = db.session.query(User).filter(User.EmailAdress == email).one_or_none()

        if user and user.passwordHash == password:
            session["user_id"] = user.id
            session["user_name"] = user.UserName

            return redirect(url_for('index'))  
        else:
            return render_template('login.html', error="Invalid credentials.")
    
    return render_template('login.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = hash_password(request.form['password'])

        try:
            new_user = User(password, email, username)
            db.session.add(new_user)
            db.session.commit()
        except:
            return render_template('register.html', error="Email already in use.")

        return redirect(url_for('login'))

    return render_template('register.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('login'))  

if __name__ == '__main__':
    app.run(debug=True)
