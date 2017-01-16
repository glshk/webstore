from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, IntegerField
from wtforms.validators import EqualTo, length, InputRequired, ValidationError
from flask_user import UserManager

from webstore import app
from webstore.models import User, db, db_adapter
from email.utils import parseaddr

def uniqueUser(form, field):
	if User.query.join(User.user_auth).filter_by(username=field.data).first():
		raise ValidationError('Username is already taken')

def validEmail(form, field):
	if parseaddr(field.data)[1] is None:
		raise ValidationError('Email address is not correct')

def uniqueEmail(form, field):
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('Your Email Address is already registered')


class LoginForm(FlaskForm):
    username = StringField('username', [InputRequired()])
    password = PasswordField('password', [InputRequired()])

class SUpForm(FlaskForm):
    first_name = StringField('first_name', [InputRequired()])
    last_name = StringField('last_name', [InputRequired()])
    username = StringField('username', [InputRequired(), uniqueUser])
    email = StringField('email', [validEmail], uniqueEmail)
    phone = StringField('phone')
    password = PasswordField('password', [
        InputRequired(),
        EqualTo('confirm', message="Passwords don't match")
    ])
    confirm = PasswordField('repeat_password')


class AddNewProductForm(FlaskForm):
    name = StringField('name', [InputRequired()])
    price = StringField('price', [InputRequired()])
    description = TextAreaField('description')
    brand = StringField('brand', [InputRequired()])
    category = StringField('category', [InputRequired()])
    image = StringField('image', [InputRequired()])

# class ChangeProduct(FlaskForm):


user_manager = UserManager(db_adapter, app)
