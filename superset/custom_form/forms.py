from flask import Flask, render_template, request, redirect, url_for, flash
from wtforms import Form, StringField, SelectField, validators, FileField, RadioField
from flask_appbuilder.forms import DynamicForm


class ReportUploadForm(DynamicForm):

    form_title = "Загрузка отчета по программе повышения финансовой грамотности населения"
    report_field = FileField('Выберите файл отчета', [validators.DataRequired()])
    region_field = SelectField('Выберите регион', choices=[])
    activity_field = RadioField('Направление деятельности',
                                choices=[
                                    ('1', 'Мероприятия по ПФГ для экономически активного населения и пенсионеров'),
                                    ('2', 'Внедрение ПФГ в образовательный процесс'),
                                    ('3', 'Размещение информационных материалов по ПФГ'),
                                    ('4', 'Подготовка кадров в области ПФГ'),],
                                default='1')

