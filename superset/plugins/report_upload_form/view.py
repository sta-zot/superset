# from flask import Flask, render_template, request, redirect, url_for, flash
import os
from datetime import datetime
from flask_appbuilder import expose, BaseView
from flask import (
    request,
    flash,
    jsonfy,
    g,
    curren_app as app
)
from superset.superset_typing import FlaskResponse
# from superset.views.base import BaseSupersetView

from .forms import ReportUploadForm
from .model import (
    LocationsModel,
    ObjectStorage,
    DocumentStorage
)
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.error("Custom view module loaded")

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


class ReportUploadView(BaseView):
    template_folder = TEMPLATES_DIR
    form = None
    activities = [
            ('1', 'Мероприятия по ПФГ для экономически активного населения и пенсионеров'),
            ('2', 'Внедрение ПФГ в образовательный процесс'),
            ('3', 'Размещение информационных материалов по ПФГ'),
            ('4', 'Подготовка кадров в области ПФГ'),
            ]
    message = "Отчет успешно загружен!"
    message_category = "success"
    default_view = "form_view"
    route_base = "/upload_form"
    logger.info(f"ReportUploadView class defined. Route base: {route_base}")

    @expose("/", methods=["GET", "POST"])
    def form_view(self) -> FlaskResponse:
        if not self.form:
            self.form = ReportUploadForm()
        locations = LocationsModel()
        regions = locations.get_regions()
        self.form.region_field.choices = [
            (regions.index(region), region)
            for region in regions
        ]
        self.form.activity_field.choices = self.activities
        return self.render_template("upload_report.html", form=self.form)

    @expose("/upload", methods=["POST"])
    def upload(self) -> FlaskResponse:
        if "file" not in request.files:
            return jsonfy(
                {
                    "status": "Error",
                    "message": "Не выбран файл"
                }
            ), 400  
        file = request.files["report_field"]
        if file.filename == "":
            return jsonfy(
                {
                    "status": "Error",
                    "message": "Не выбран файл"
                }
            ), 400

        if request.form.get("region_field") == "":
            return jsonfy(
                {
                    "status": "Error",
                    "message": "Не выбран регион"
                }
            ), 400
        else:
            region = request.form.get("region_field")

        if request.form.get("activity_field") == "":
            return jsonfy(
                {
                    "status": "Error",
                    "message": "Не выбрано направление деятельности"
                }
            ), 400
        else:
            activity = request.form.get("activity_field")

        comment = request.form.get("comment_field") 

        s3 = ObjectStorage(
            s3_access_key=app.config["S3_ACCESS_KEY"],
            s3_secret_key=app.config["S3_SECRET_KEY"],
            bucket_name=app.config["S3_BUCKET"],
            endpoint_url=app.config["S3_ENDPOINT_URL"]
        )
        ds = DocumentStorage(
            host=app.config["DS_HOST"],
            port=app.config["DS_PORT"],
            username=app.config["DS_USER"],
            password=app.config["DS_PASSWD"],
            database=app.config["DS_DB"]
        )

        try:
            s3.add(file, prefix=activity.title())
        except Exception as e:
            logger.error(f"Error uploading file to S3: {e}")
            return jsonfy(
                {
                    "status": "Error",
                    "message": "Ошибка загрузки файла"
                }
            ), 500
        try:
            ds.add(
                {
                    "author": g.user,
                    "region": region,
                    "activity": {
                        "id": activity.title(),
                        "title": self.activities[activity.title()]
                        },
                    "created_at": datetime.now().timestamp(),
                    "comment": comment,
                    "prefix": activity.title(),
                    "filename": file.filename,
                }
            )
        except Exception as e:
            logger.error(f"Error adding report to DB: {e}")
            return jsonfy(
                {
                    "status": "Error",
                    "message": "Ошибка загрузки файла"
                }
            ), 500
        return jsonfy(
            {
                "status": "Success",
                "message": "Файл успешно загружен"
            }
        ), 200
