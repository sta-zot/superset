from flask import Flask, render_template, request, redirect, url_for, flash
from flask_appbuilder import SimpleFormView, expose
from superset.superset_typing import FlaskResponse
from superset.views.base import BaseSupersetView

from .forms import ReportUploadForm
from .model import LocalesModel
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.error("Custom view module loaded")

class ReportUploadView(BaseSupersetView):
    form = None
    choices = [
            ('1', 'Мероприятия по ПФГ для экономически активного населения и пенсионеров'),
            ('2', 'Внедрение ПФГ в образовательный процесс'),
            ('3', 'Размещение информационных материалов по ПФГ'),
            ('4', 'Подготовка кадров в области ПФГ'),
            ]
    message = "Отчет успешно загружен!"
    message_category = "success"
    route_base = "/upload_report"
    logger.info(f"ReportUploadView class defined. Route base: {route_base}")

    @expose("/", methods=["GET", "POST"])
    def form_view(self) -> FlaskResponse:
        if not self.form:
            self.form = ReportUploadForm()
        locations = LocalesModel.get_regions()
        self.form.region_field.choices = [
            (locations.index(location), location) for location in locations
        ]
        self.form.activity_field.choices = self.choices
        return self.render_template("upload_report.html")


    # def form_get(self, form: ReportUploadForm) -> None:
    #     form.actyvity_field.data = '1'

    # def form_post(self, form: ReportUploadForm) -> FlaskResponse:
    #     # Логика обработки загруженного файла и других данных формы
    #     report_file = request.files[form.report.name]
    #     actyvity_field = form.actyvity_field.data
    #     # Здесь можно добавить код для сохранения файла в объектное хранилище
    #     flash(self.message, self.message_category)
    #     flash(report_file.filename, self.message_category)
    #     flash(actyvity_field, self.message_category)
    #     return redirect(url_for("ReportUploadView.form"))
