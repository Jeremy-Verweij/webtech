import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
import os
import hashlib

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
    return render_template('index.html', user_name=session['user_name'])

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

@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('login'))  

if __name__ == '__main__':
    app.run(debug=True)
