from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length

from app.models import User, Role


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    location = StringField('Location', validators=[Length(0, 64)])
    # TextAreaField is a multiline box
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired()])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int) # cast to int from str
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user # to compare old user with new user fields

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise  ValidationError('Username already in use')