"""
В этом файле можно определить пользовательские формы для Superset.
Формы предназначены для загрузки отчетов в объектное хранилище.
"""


from .model import LocalesModel
from .forms import ReportUploadForm
from .wiew import ReportUploadView
