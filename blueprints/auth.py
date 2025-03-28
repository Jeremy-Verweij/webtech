from flask import Blueprint,render_template,redirect, request, session, url_for
from forms.login import LoginForm
from forms.register import RegistrationForm
from setup import db
from models import *
from utils.hash_password import hash_password

auth_blueprint = Blueprint("auth", __name__, template_folder="templates", url_prefix="/auth")

# Login
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = hash_password(form.password.data)
        print(email, password)
        
        user = db.session.query(User).filter(User.EmailAdress == email).one_or_none()

        if user and user.passwordHash == password:
            session["user_id"] = user.id
            session["user_name"] = user.UserName
            session.modified = True
            
            return redirect(url_for('index'))  
        else:
            form.email.errors.append("Invalid credentials.")
    
    return render_template('login.html', form=form)

# Register
@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    
    if request.method == 'POST' and form.validate():
        email = form.email.data
        username = form.username.data
        password = hash_password(form.password.data)
        
        try:
            new_user = User(password, email, username)
            db.session.add(new_user)
            db.session.commit()
        except:
            form.email.errors.append("Email already in use.")
            return render_template('register.html', form=form)

        user = db.session.query(User).filter(User.EmailAdress == email).one_or_none()
        session["user_id"] = user.id
        session["user_name"] = user.UserName
        session.modified = True
        
        return redirect(url_for('index'))  

    return render_template('register.html', form=form)

# Logout
@auth_blueprint.route('/logout')
def logout():
    session.clear()  
    session.modified = True
    return redirect(url_for('auth.login'))  
