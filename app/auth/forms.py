from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User

class LoginForm(FlaskForm):
    # username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')  # checkbox
    submit = SubmitField('Sign in')



class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1,64)])  # requires dependency email-validator
    password = StringField('Password', validators=[DataRequired()])
    password2 = StringField('Repeat Password', validators=[DataRequired(), EqualTo('password', message="passwords must match")]) # validator takes fileld name as string not the field object
    submit = SubmitField('Register')

    # validate_<field_name> are custom validators of WTForms, that are invoked in addition to regularly defined validators
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(f'Username {username} was taken, use another')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(f'Email {email} already registered')
