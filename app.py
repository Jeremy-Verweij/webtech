import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

db_path = 'database/db.sqlite'

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))  
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Users WHERE EmailAdress = ? AND PasswordHash = ?', (email, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['UUID'] 
            session['user_name'] = user['UserName'] 
            return redirect(url_for('index'))  
        else:
            return render_template('login.html', error="Ongeldige inloggegevens.")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('login'))  

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login')) 
    return render_template('dashboard.html', user_name=session['user_name'])

if __name__ == '__main__':
    app.run(debug=True)
