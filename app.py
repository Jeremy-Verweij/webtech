import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import hashlib
import base64

app = Flask(__name__)
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

    conn = get_db_connection()
    posts = conn.execute("""
        SELECT Posts.PostID, Posts.Title, Posts.Content, Users.UserName, Users.ProfilePicture,
               (SELECT COUNT(*) FROM Likes WHERE Likes.PostID = Posts.PostID) AS Likes
        FROM Posts
        JOIN Users ON Posts.UserID = Users.UUID
        ORDER BY Posts.PostID DESC
    """).fetchall()

    conn.close()
    return render_template('index.html', user_name=session['user_name'], posts=posts)

# Create Post
@app.route('/create_post', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form.get('title')
    content = request.form.get('content')

    conn = get_db_connection()
    conn.execute("INSERT INTO Posts (UserID, Title, Content) VALUES (?, ?, ?)",
                 (session['user_id'], title, content))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# Like Post
@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    existing_like = conn.execute("SELECT * FROM Likes WHERE UserID = ? AND PostID = ?", 
                                 (session['user_id'], post_id)).fetchone()
    
    if existing_like:
        conn.execute("DELETE FROM Likes WHERE UserID = ? AND PostID = ?", 
                     (session['user_id'], post_id))  # Unlike
    else:
        conn.execute("INSERT INTO Likes (UserID, PostID) VALUES (?, ?)", 
                     (session['user_id'], post_id))  # Like

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Follow/Unfollow User
@app.route('/follow/<int:user_id>', methods=['POST'])
def follow_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    already_following = conn.execute("SELECT * FROM Following WHERE UserID = ? AND FollowedUserID = ?", 
                                     (session['user_id'], user_id)).fetchone()

    if already_following:
        conn.execute("DELETE FROM Following WHERE UserID = ? AND FollowedUserID = ?", 
                     (session['user_id'], user_id))  # Unfollow
    else:
        conn.execute("INSERT INTO Following (UserID, FollowedUserID) VALUES (?, ?)", 
                     (session['user_id'], user_id))  # Follow

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Repost
@app.route('/repost/<int:post_id>', methods=['POST'])
def repost(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute("INSERT INTO Posts (UserID, RepostID) VALUES (?, ?)", 
                 (session['user_id'], post_id))
    conn.commit()
    conn.close()
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

# Change Language Setting
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
    
    return redirect(url_for('index'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Users WHERE EmailAdress = ? AND PasswordHash = ?', (email, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['UUID'] 
            session['user_name'] = user['UserName'] 
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

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO Users (PasswordHash, EmailAdress, UserName) VALUES (?, ?, ?)", 
                         (password, email, username))
            conn.commit()
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Email already in use.")
        finally:
            conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('login'))  

if __name__ == '__main__':
    app.run(debug=True)
