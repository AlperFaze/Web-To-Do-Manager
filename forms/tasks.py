from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.fields.datetime import DateTimeLocalField
from wtforms.validators import DataRequired


class TasksForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    deadline = DateTimeLocalField('Дедлайн', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Применить')