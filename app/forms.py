from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL
from wtforms.validators import Length
from wtforms import SelectField

PHRASE_MAX_LEN = 200

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class TextForReadingForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    url = StringField("Source URL", validators=[Optional(), URL()])
    submit = SubmitField("Save Text")

class TrainingListForm(FlaskForm):
    name = StringField("List name", validators=[DataRequired()])
    lang_from = SelectField('From Language', choices=[], validators=[DataRequired()])
    lang_to = SelectField('To Language', choices=[], validators=[DataRequired()])
    submit = SubmitField("Create List")

class TrainingItemForm(FlaskForm):
    phrase = StringField("Phrase", validators=[DataRequired()])
    translation = TextAreaField("Translation", validators=[DataRequired()])
    context = TextAreaField("Context (optional)", validators=[Optional()])
    submit = SubmitField("Add Item")

class TrainingItemWithListForm(FlaskForm):
    list_name = StringField("List name", validators=[DataRequired()])
    phrase = StringField("Phrase", validators=[DataRequired(), Length(max=PHRASE_MAX_LEN)])
    translation = TextAreaField("Translation", validators=[DataRequired()])
    context = TextAreaField("Context (optional)", validators=[Optional()])
    submit = SubmitField("Add Item")

