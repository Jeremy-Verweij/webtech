from flask import Blueprint,render_template,redirect, request, session, url_for
from setup import db
from models import *
from utils.hash_password import hash_password

auth_blueprint = Blueprint("auth", __name__, template_folder="templates", url_prefix="/auth")

# Login
@auth_blueprint.route('/login', methods=['GET', 'POST'])
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
@auth_blueprint.route('/register', methods=['GET', 'POST'])
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

        return redirect(url_for('auth.login'))

    return render_template('register.html')

# Logout
@auth_blueprint.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('auth.login'))  
