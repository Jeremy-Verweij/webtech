from wtforms import Form, StringField, PasswordField, validators

class RegistrationForm(Form):
    username = StringField('Username', [
        validators.Length(min=4, max=25),
        validators.InputRequired("Username is required")
    ])
    email = StringField('Email Address', [
        validators.Length(min=6, max=35),
        validators.Email(),
        validators.InputRequired("Email is required")
    ])
    password = PasswordField('New Password', [
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.Length(min=8, max=64),
        validators.Regexp("(?=.*\d)(?=.*[a-z])(?=.*[A-Z])", message="Password must contain at least one number, one lowercase and one uppercase."),
        validators.InputRequired("Password is required")
    ])
    confirm = PasswordField('Repeat Password')