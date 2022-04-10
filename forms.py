from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,  BooleanField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


##WTForm
class CreateForm(FlaskForm):
    name = StringField("Cafe Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    has_sockets = BooleanField("Has Socket",)
    has_toilet = BooleanField("Has Toilet", )
    has_wifi = BooleanField("Has Wifi",)
    can_take_calls = BooleanField("Can take calls",)
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    map_url = StringField("Map URL", validators=[DataRequired(), URL()])
    seats = StringField('Number of Seats')
    coffee_price = StringField('Coffee Price', [DataRequired(),])
    comment = StringField('Comment', [DataRequired(),])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField()



class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")
