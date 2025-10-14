from flask import Flask, render_template, request, redirect, url_for, flash
from flask_appbuilder import SimpleFormView, expose
from superset.superset_typing import FlaskResponse

from .forms import ReportUploadForm
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.error("Custom view module loaded")

class ReportUploadView(SimpleFormView):
    form = ReportUploadForm
    form_title = "Загрузка отчета по программе повышения финансовой грамотности населения"
    message = "Отчет успешно загружен!"
    message_category = "success"
    base_url = "/report_upload"
    # @expose("/", methods=["GET", "POST"])
    # def upload_report(self):
    #     if request.method == "POST":
    #         form = self.form(request.form)
    #         if form.validate():
    #             # Логика обработки загруженного файла и других данных формы
    #             report_file = request.files[form.report.name]
    #             actyvity_field = form.actyvity_field.data
    #             # Здесь можно добавить код для сохранения файла в объектное хранилище
    #             flash(self.message, self.message_category)
    #             return redirect(url_for("ReportUploadView.upload_report"))
    #     else:
    #         form = self.form()
    #     return self.render_template(self.template, form=form)

    def form_get(self, form: ReportUploadForm) -> None:
        form.actyvity_field.data = '1'

    def form_post(self, form: ReportUploadForm) -> FlaskResponse:
        # Логика обработки загруженного файла и других данных формы
        report_file = request.files[form.report.name]
        actyvity_field = form.actyvity_field.data
        # Здесь можно добавить код для сохранения файла в объектное хранилище
        flash(self.message, self.message_category)
        flash(report_file.filename, self.message_category)
        flash(actyvity_field, self.message_category)
        return redirect(url_for("ReportUploadView.form"))