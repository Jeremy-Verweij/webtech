from wtforms import Form, StringField, PasswordField, validators

class LoginForm(Form):
    email = StringField('Email Address', [
        validators.Length(min=6, max=35),
        validators.Email(),
        validators.InputRequired("Email is required")
        ])
    
    password = PasswordField('Password', [
        validators.InputRequired(message="Password is required")
    ])
    