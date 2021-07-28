from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length

class RegisterUserForm(FlaskForm):
    username = StringField('Username', validators = [InputRequired(), Length(max=20)])
    password = PasswordField('Password', validators = [InputRequired()])
    email = StringField('Email', validators = [InputRequired(), Email(), Length(max=50)])
    first_name = StringField('First name', validators = [InputRequired(), Length(max=30)])
    last_name = StringField('Last name', validators = [InputRequired(), Length(max=30)])

class LoginUserForm(FlaskForm):
    username = StringField('Username', validators = [InputRequired(), Length(max=20)])
    password = PasswordField('Password', validators = [InputRequired()])