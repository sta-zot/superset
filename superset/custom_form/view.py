from flask import Flask, render_template, request, redirect, url_for, flash
from flask_appbuilder import SimpleFormView, expose
from superset.superset_typing import FlaskResponse
from superset.views.base import SupersetBaseView

from .forms import ReportUploadForm
from .model import LocalesModel
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.error("Custom view module loaded")

class ReportUploadView(SupersetBaseView):
    form = ReportUploadForm
    form_title = "Загрузка отчета по программе повышения финансовой грамотности населения"
    message = "Отчет успешно загружен!"
    message_category = "success"
    route_base = "/upload_report"
    
    logger.info(f"ReportUploadView class defined. Route base: {route_base}")
    @expose("/", methods=["GET", "POST"])
    def form_view(self) -> FlaskResponse:
        locations = LocalesModel.get_regions()
        self.form.region_field.choices = [(loc['id'], loc['name']) for loc in locations]
        



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