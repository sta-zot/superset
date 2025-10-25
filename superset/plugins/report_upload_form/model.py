# """
# В этом модуле определяются модели для работы с базами данных для пользовательских форм.
# """
# import logging
# import pandas as pd
# import boto3
# from typing import List, Any, BinaryIO
# from werkzeug.datastructures import FileStorage


# class LocationsModel():

#     def __init__(self, locale: str = "en"):
#         self.locale = locale
#         self.locales = self.__load_locales()

#     def __load_locales(self):
#         try:
#             locales = pd.read_csv("https://raw.githubusercontent.com/sta-zot/SRW/refs/heads/main/data/locations.csv")
#         except Exception as e:
#             logging.error(f"Error loading locales: {e}")
#             locales = pd.DataFrame({
#                 "region": ["Рязанская область", "Московская область","Ленинградская область"],
#                 "municipality": ["Рязанcский район", "Московский район","Ленинградский район"],
#                 "settlement": ["г. Рязань", "г. Москва","г. Санкт-Петербург"]
#             })
#         return locales

#     def get_regions(self):
#         return self.locales["region"].unique().tolist()

#     def get_municipalities(self, region: str):
#         return self.locales[self.locales["region"] == region]["municipality"].unique().tolist()

#     def get_settlements(self, municipality: str):
#         if municipality == "":
#             return (self.locales["type"] + '. ' + self.locales["settlement"]).tolist()
#         filtered_df = self.locales[self.locales["municipality"] == municipality]
#         # print(filtered_df.count())
#         return (filtered_df["type"] + '. ' + filtered_df["settlement"]).unique().tolist()

#     def get_df(self)-> pd.DataFrame:
#         return self.locales


# class ObjectStorage():
#     def __init__(
#             self,
#             s3_access_key: str,
#             s3_secret_key: str,
#             endpoint_url: str,
#             bucket_name: str,
#     ):
#         """
#         Инициализация клиента для работы с объектным хранилищем S3
#         :param s3_access_key: Ключ доступа к S3.
#         :param s3_secret_key: Секретный ключ доступа к S3.
#         :param endpoint_url: URL-адрес S3.
#         :param bucket_name: Название бакета S3.
#         :return: None
#         :raises ValueError: Если не указаны все необходимые параметры для работы с S3.
#         :raises Exception: Если произошла ошибка при инициализации клиента S3.
#         :example:
#         >>> s3_client = ObjectStor(
#         >>>     s3_access_key="your_access_key",
#         >>>     s3_secret_key="your_secret_key",
#         >>>     endpoint_url="XXXXXXXXXXXXXXXXXXXXXXXXX",
#         >>>     bucket_name="your_bucket_name",
#         >>> )
#         >>> # Теперь вы можете использовать s3_client для работы с S3
#         >>> s3_client.list_buckets().
#         """
#         if not all([s3_access_key, s3_secret_key, endpoint_url, bucket_name]):
#             raise ValueError("All parameters must be provided for S3 initialization.")
        
#         self.client = boto3.client(
#             's3',
#             aws_access_key_id=s3_access_key,
#             aws_secret_access_key=s3_secret_key,
#             endpoint_url=endpoint_url,
#             region_name='us-east-1',
#         )
#         self.bucket_name = bucket_name
#         if not self.__has_bucket():
#             self.create_bucket()

#     def create_bucket(self) -> None:
#         self.client.create_bucket(Bucket=self.bucket_name)

#     def __has_bucket(self) -> bool:
#         try:
#             self.client.head_bucket(Bucket=self.bucket_name)
#             return True
#         except self.client.exceptions.NoSuchBucket:
#             return False

#     def add(
#             self,
#             file: FileStorage | list[FileStorage],
#             prefix: str = "",
#             *args,
#             **kwargs
#     ) -> None:
#         """
#         Upload file to S3 bucket.
#         :param file: FileStorage object or list of FileStorage objects
#         :param prefix: prefix for file name
#         :param args: additional arguments, not used
#         :param kwargs: additional keyword arguments, used for add metadata during file upload
#         :return: None
#         :exception ValueError: if file is not FileStorage object or list of FileStorage objects
#         """

#         if isinstance(file, list):
#             for f in file:
#                 key = f'{prefix}/{file.filename}' if prefix else file.filename
#                 self.client.upload_fileobj(
#                     f,
#                     self.bucket_name,
#                     key,
#                     #ExtraArgs={"Metadata": kwargs} if kwargs else None, не заморачиваемся с метаданными пока
#                     # minio не поддерживает кодировку метаданных в utf-8
#                 )
#         else:
#             key = f'{prefix}/{file.filename}' if prefix else file.filename
#             self.client.upload_fileobj(
#                 file,
#                 self.bucket_name,
#                 key,
#                 #ExtraArgs={"Metadata": kwargs} if kwargs else None, не заморачиваемся с метаданными пока
#                 # minio не поддерживает кодировку метаданных в utf-8
#             )

#     def get(self, file_name: str) -> BinaryIO:
#         """
#         Возвращает объект совместимый с объектом file в виде потока байт
#         Args:
#             file_name (str): имя файла для скачивания

#         Returns:
#             BinaryIO: Объект типа StreamingBody имеющий интерфейс как у объекта file
#         """
#         response = self.client.get_object(
#             bucket=self.bucket_name,
#             Key=file_name)
#         return response['Body']

#     def list(self, prefix: str = "") -> list:
#         """Возвращает список файлов 
#         Args:
#             prefix: Уловная директория из которой 
#             надо получить список файлов. По умолчанию 
#             пустая строка
#         Returns:
#             list: Список имён файлов
#         """
#         response = self.client.list_objects_v2(
#             Bucket=self.bucket_name,
#             prefix=prefix
#         )

#         if 'Contents' in response:
#             return [item['Key'] for item in response['Contents']]
#         return []

#     def list_buckets(self):
#         """
#         Получение списка бакетов S3.
#         :return: Список бакетов S3.
#         :raises Exception: Если произошла ошибка при получении списка бакетов.
#         :example:
#         >>> s3_client = ObjectStor(
#         >>>     s3_access_key="your_access_key",
#         >>>     s3_secret_key="your_secret_key",
#         >>>     endpoint_url="XXXXXXXXXXXXXXXXXXXXXXXXX",
#         >>>     bucket_name="XXXXXXXXXXXXXXXX",
#         >>> )
#         >>> buckets = s3_client.list_buckets()
#         >>> print(buckets)
#         """
#         try:
#             response = self.client.list_buckets()
#             return response['Buckets']
#         except Exception as e:
#             raise Exception(f"Error listing buckets: {e}") from e


# class DocumentStorage():
#     def __init__(
#         self,
#         host: str,
#         port: int,
#         username: str,
#         password: str,
#         database: str
#     ) -> None:
#         if not all([host, port, username, password, database]):
#             raise ValueError("All parameters must be provided")
#         self.db_client = pymongo.MongoClient(
#             host=host,
#             port=port,
#             username=username,
#             password=password
#         )
#         #Проводить проверку на наличие БД не нужно, если её нет то она создастся
#         self.db = self.db_client[database]
#         self.db_collection = self.db["reports"]

#     def add(
#         self,
#         data: dict,
#         collection: str = "",
#     ) -> None:
#         if not collection:
#             db_collection = self.db_collection
#         else:
#             db_collection = self.db[collection]

#         db_collection.insert_one(data)

#     def add_many(
#         self,
#         data: dict,
#         collection: str = "",
#     ) -> None:

#         if not collection:
#             db_collection = self.db_collection
#         else:
#             db_collection = self.db[collection]

#         db_collection.insert_one(data)

#     def get(
#         self,
#         filter: dict,
#         collection: str = "",
#     ) -> dict:
#         if not collection:
#             db_collection = self.db_collection
#         else:
#             db_collection = self.db[collection]
#         return db_collection.find_one(filter)

#     def list(
#         self,
#         filter: dict = None,
#         collection: str = "",
#     ) -> list:
#         if not collection:
#             db_collection = self.db_collection
#         else:
#             db_collection = self.db[collection]
#         if filter:
#             return [item for item in db_collection.find(filter)]
#         return [item for item in db_collection.find()]


# # if __name__ == "__main__":
# #     pass  
