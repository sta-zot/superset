# from flask import Flask, render_template, request, redirect, url_for, flash
from flask_appbuilder import expose, BaseView
from superset.superset_typing import FlaskResponse
# from superset.views.base import BaseSupersetView

from .forms import ReportUploadForm
from .model import LocationsModel
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.error("Custom view module loaded")


class ReportUploadView(BaseView):
    form = None
    choices = [
            ('1', 'Мероприятия по ПФГ для экономически активного населения и пенсионеров'),
            ('2', 'Внедрение ПФГ в образовательный процесс'),
            ('3', 'Размещение информационных материалов по ПФГ'),
            ('4', 'Подготовка кадров в области ПФГ'),
            ]
    message = "Отчет успешно загружен!"
    message_category = "success"
    default_view = "form_view"
    route_base = "/upload_report"
    logger.info(f"ReportUploadView class defined. Route base: {route_base}")

    @expose("/", methods=["GET", "POST"])
    def form_view(self) -> FlaskResponse:
        if not self.form:
            self.form = ReportUploadForm()
        locations = LocationsModel()
        locations = locations.get_regions()
        # self.form.region_field.choices = [
        #     (locations.index(location), location)
        #     for location in locations
        # ]
        self.form.region_field.choices = [
            "variant 1",
            "variant 2"
        ]
        self.form.activity_field.choices = self.choices
        return self.render_template("upload_report.html", form=self.form)
