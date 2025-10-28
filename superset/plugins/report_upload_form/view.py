# from flask import Flask, render_template, request, redirect, url_for, flash
import os
from datetime import datetime
from flask_appbuilder import expose, BaseView
from flask_appbuilder.security.decorators import protect
from flask import (
    request,
    flash,
    jsonify,
    g,
    current_app as app
)
from dotenv import load_dotenv
from superset.superset_typing import FlaskResponse
from superset.views.base import BaseSupersetView

from .forms import ReportUploadForm
from .model import (
   LocationsModel,
   ObjectStorageModel,
   DocumentStorageModel
)
import logging


load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.error("Custom view module loaded")

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


class ReportUploadView(BaseView):
    template_folder = TEMPLATES_DIR
    form = None
    
    activities = {
        '1': 'Мероприятия по ПФГ для экономически активного населения и пенсионеров',
        '2': 'Внедрение ПФГ в образовательный процесс',
        '3': 'Размещение информационных материалов по ПФГ',
        '4': 'Подготовка кадров в области ПФГ',
    }
    
    default_view = "form_view"
    route_base = "/upload_form"
    static_folder = STATIC_DIR
    logger.info(f"ReportUploadView class defined. Route base: {route_base}")


    @expose("/", methods=["GET"])
    def form_view(self) -> FlaskResponse:
        locations = LocationsModel()
        if not self.form:
            self.form = ReportUploadForm()
        self.form.region_field.choices =  locations.get_regions()
        self.form.activity_field.choices = list(self.activities.items())
        self.form.activity_field.default = 1
        self.form.activity_field.process(formdata=None)
        return self.render_template("upload_report.html", form=self.form)

    @expose("/upload", methods=["POST"])
    def upload(self) -> FlaskResponse:
        locations = LocationsModel()
        try:
            if "report_field" not in request.files:
                return jsonify(
                    {
                        "status": "error",
                        "message": "Не выбран файл"
                    }
                ), 400
            file = request.files["report_field"]
            if file.filename == "":
                return jsonify(
                    {
                        "status": "error",
                        "message": "Не выбран файл"
                    }
                ), 400
            if request.form.get("region_field") == "":
                return jsonify(
                    {
                        "status": "error",
                        "message": "Не выбран регион"
                    }
                ), 400
            else:
                region = request.form.get("region_field")
            if request.form.get("activity_field") == "":
                return jsonify(
                    {
                        "status": "error",
                        "message": "Не выбрано направление деятельности"
                    }
                ), 400
            else:
                activity = request.form.get("activity_field")
            comment = request.form.get("comment_field")
        except Exception as e:
            app.logger.error(f"Upload error: {e}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": f"Ошибка на сервере: {e}"
            }), 500
        filename = file.filename.lower()    
        config = {
            "DS_HOST": os.getenv("DS_HOST"),
            "DS_PORT": os.getenv("DS_PORT"),
            "DS_USER": os.getenv("DS_USER"),
            "DS_PASSWD": os.getenv("DS_PASSWD"),
            "DS_DB": os.getenv("DS_DB"),
            "S3_ACCESS_KEY": os.getenv("S3_ACCESS_KEY"),
            "S3_SECRET_KEY": os.getenv("S3_SECRET_KEY"),
            "S3_BUCKET": os.getenv("S3_BUCKET"),
            "S3_ENDPOINT_URL": os.getenv("S3_ENDPOINT_URL")
        }
        if not all(v not in (None, '') for v in config.values()):
            return jsonify(
                 {
                    "status": 'error',
                    "message": f"Не все переменные для подключения доступны"
                }
            ), 400
            
        try:       
            s3 = ObjectStorageModel(
                s3_access_key=config["S3_ACCESS_KEY"],
                s3_secret_key=config["S3_SECRET_KEY"],
                bucket_name=config["S3_BUCKET"],
                endpoint_url=config["S3_ENDPOINT_URL"]
            )
        except Exception as e:
            return jsonify(
                {
                    "status": 'error',
                    "message": f"S3 connection to {config['S3_ENDPOINT_URL']} error {e}"
                }
            ), 500
        try:
            ds = DocumentStorageModel(
                host=config["DS_HOST"],
                port=int(config["DS_PORT"]),
                username=config["DS_USER"],
                password=config["DS_PASSWD"],
                database=config["DS_DB"]
            )
        except Exception as e:
            app.logger.error(f"Upload error: {e}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": f"Ошибка при создании подключения к хранилищу:<br> {e}"
            }), 500
        

        try:
            s3.add(file, prefix=activity)
        except Exception as e:
            logger.error(f"Error uploading file to S3: {e}")
            return jsonify(
                {
                    "status": "error",
                    "message": "Ошибка загрузки файла"
                }
            ), 500
        try:
            ds.add(
                {
                    "author": (
                        f"{getattr(g.user, 'first_name', '')} {getattr(g.user, 'last_name', '')}"
                    ).strip() or getattr(g.user, 'username', str(g.user)),
                    "region": locations.get_region(int(region)),
                    "activity": {
                        "id": activity,
                        "title": self.activities[activity]
                        },
                    "created_at": datetime.now().timestamp(),
                    "comment": comment,
                    "prefix": activity,
                    "filename": filename,
                    "status": "new"
                }
            )
        except Exception as e:
            logger.error(f"Error adding report to DB: {e}")
            return jsonify(
                {
                    "status": "error",
                    "message": "Ошибка загрузки файла"
                }
            ), 500
        return jsonify(
            {
                "status": "success",
                "message": f"Файл {file.filename} успешно загружен"
            }
        ), 200
