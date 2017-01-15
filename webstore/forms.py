from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, IntegerField
from wtforms.validators import EqualTo, length, InputRequired
# from validators import uniqueUser, validEmail


class LoginForm(FlaskForm):
    username = StringField('username', [InputRequired()])
    password = PasswordField('password', [InputRequired()])


# class SingupForm(FlaskForm):
#     first_name = StringField('first_name', [InputRequired()])
#     last_name = StringField('last_name', [InputRequired()])
#     username = StringField('username', [InputRequired(), uniqueUser])
#     email = StringField('email', [validEmail])
#     phone = StringField('phone')
#     password = PasswordField('password', [
#         InputRequired(),
#         EqualTo('confirm', message="Passwords don't match")
#     ])
#     confirm = PasswordField('repeat_password')


class AddNewProductForm(FlaskForm):
    name = StringField('name', [InputRequired()])
    price = StringField('price', [InputRequired()])
    description = TextAreaField('description')
    brand = StringField('brand', [InputRequired()])
    category = StringField('category', [InputRequired()])
    image = StringField('image', [InputRequired()])

# class ChangeProduct(FlaskForm):