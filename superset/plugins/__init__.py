    """
        Для работы плагина требуется добавить переменные окружения:
            S3_BUCKET_NAME = "Названи бакета"
            S3_SECRET_KEY = "minioadmin"
            S3_ACCESS_KEY = "minioadmin"
            S3_ENDPOINT_URL = "http://minio_url:9000"

            MONGO_HOST = "mongodb_url"
            MONGO_PORT = 27017
            MONGO_DB = "Название базы данных"
            MONGO_USER = "mongoadmin"
            MONGO_PASSWORD = "mongoadminpasswd"
        Сделано
        Настроить получение переменных окружения:
        сделано через docker\pythonpath_dev\superset_config.py
        
    """

from .report_upload_form import (
    LocationsModel,
    ReportUploadForm,
    ReportUploadView,
    ObjectStorage,
    DocumentStorage
) # noqa: F401
