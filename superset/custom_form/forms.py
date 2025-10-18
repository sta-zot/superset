from flask import Flask, render_template, request, redirect, url_for, flash
from wtforms import Form, StringField, SelectField, validators, FileField, RadioField
from flask_appbuilder.forms import DynamicForm


class ReportUploadForm(DynamicForm):

    title = "Загрузка отчета по программе повышения финансовой грамотности населения"
    report_field = FileField('Выберите файл отчета', [validators.DataRequired()])
    region_field = SelectField('Выберите регион', choices=[])
    activity_field = RadioField('Направление деятельности',
                                choices=[],
                                default='1')

