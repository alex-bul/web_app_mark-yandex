from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class JobForm(FlaskForm):
    job = StringField('Название работы', validators=[DataRequired()])
    work_size = DecimalField('Длительность (в часах)', validators=[DataRequired()])
    collaborators = StringField('Колабораторы', validators=[DataRequired()])
    # start_date = DateTimeField("Дата начала", validators=[DataRequired()])
    # end_date = DateTimeField("Дата конца", validators=[DataRequired()])
    is_finished = BooleanField("Работа завершена?")
    submit = SubmitField('Создать')