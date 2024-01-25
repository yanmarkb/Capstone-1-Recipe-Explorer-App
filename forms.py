from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, URL, ValidationError, InputRequired, AnyOf, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # Add optional string fields for the image URL, header image URL, bio, and location.
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    bio = StringField('(Optional) Bio')
    location = StringField('(Optional) Location')

class LoginForm(FlaskForm):
    """Login form."""

    # Add a string field for the username, which is required.
    username = StringField('Username', validators=[DataRequired()])

    # Add a password field for the password, which must be at least 6 characters long.
    password = PasswordField('Password', validators=[Length(min=6)])

    submit = SubmitField('Login')