"""
В этом файле можно определить пользовательские формы для Superset.
Формы предназначены для загрузки отчетов в объектное хранилище.
"""
# from .model import (
#     LocationsModel,
#     ObjectStorage,
#     DocumentStorage
# ) # noqa: F401
# from .forms import ReportUploadForm # noqa: F401
from .view import ReportUploadView, STATIC_DIR # noqa: F401
import logging

logging.warning("Custom form module initialized")
