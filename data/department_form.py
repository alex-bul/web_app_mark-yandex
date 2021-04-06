from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired


class DepartmentForm(FlaskForm):
    title = StringField('Название департамента', validators=[DataRequired()])
    members = StringField('Участники', validators=[DataRequired()])
    email = StringField('Эмейл', validators=[DataRequired()])
    submit = SubmitField('Создать')