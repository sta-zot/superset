"""
В этом модуле определяются модели для работы с базами данных для пользовательских форм.
"""
#import json
import logging

import pandas as pd

import boto3
from typing import List, Any
from werkzeug.datastructures import FileStorage


class LocationsModel():

    def __init__(self, locale: str = "en"):
        self.locale = locale
        self.locales = self.__load_locales()

    def __load_locales(self):
        try:
            locales = pd.read_csv("https://raw.githubusercontent.com/sta-zot/SRW/refs/heads/main/data/locations.csv")
        except Exception as e:
            logging.error(f"Error loading locales: {e}")
            locales = pd.DataFrame({
                "region": ["Рязанская область", "Московская область","Ленинградская область"],
                "municipality": ["Рязанcский район", "Московский район","Ленинградский район"],
                "settlement": ["г. Рязань", "г. Москва","г. Санкт-Петербург"]
            })
        return locales

    def get_regions(self):
        return self.locales["region"].unique().tolist()

    def get_municipalities(self, region: str):
        return self.locales[self.locales["region"] == region]["municipality"].unique().tolist()

    def get_settlements(self, municipality: str):
        if municipality == "":
            return (self.locales["type"] + '. ' + self.locales["settlement"]).tolist()
        filtered_df = self.locales[self.locales["municipality"] == municipality]
        # print(filtered_df.count())
        return (filtered_df["type"] + '. ' + filtered_df["settlement"]).unique().tolist()

    def get_df(self)-> pd.DataFrame:
        return self.locales



class ObjectStor():
    def __init__(
            self,
            s3_access_key: str |None = None,
            s3_secret_key: str | None  = None,
            endpoint_url: str | None  = None,
            bucket_name: str | None  = None,
    ):
        """
        Инициализация клиента для работы с объектным хранилищем S3
        :param s3_access_key: Ключ доступа к S3.
        :param s3_secret_key: Секретный ключ доступа к S3.
        :param endpoint_url: URL-адрес S3.
        :param bucket_name: Название бакета S3.
        :return: None
        :raises ValueError: Если не указаны все необходимые параметры для работы с S3.
        :raises Exception: Если произошла ошибка при инициализации клиента S3.
        :example:
        >>> s3_client = ObjectStor(
        >>>     s3_access_key="your_access_key",
        >>>     s3_secret_key="your_secret_key",
        >>>     endpoint_url="XXXXXXXXXXXXXXXXXXXXXXXXX",
        >>>     bucket_name="your_bucket_name",
        >>> )
        >>> # Теперь вы можете использовать s3_client для работы с S3
        >>> s3_client.list_buckets().
        """
        if not all([s3_access_key, s3_secret_key, endpoint_url, bucket_name]):
            raise ValueError("All parameters must be provided for S3 initialization.")
        
        self.s3_client = boto3.client(
            's3',
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            endpoint_url=endpoint_url,
            bucket=bucket_name,
        )
        self.bucket_name = bucket_name
    
    def list_buckets(self):
        """
        Получение списка бакетов S3.
        :return: Список бакетов S3.
        :raises Exception: Если произошла ошибка при получении списка бакетов.
        :example:
        >>> s3_client = ObjectStor(
        >>>     s3_access_key="your_access_key",
        >>>     s3_secret_key="your_secret_key",
        >>>     endpoint_url="XXXXXXXXXXXXXXXXXXXXXXXXX",
        >>>     bucket_name="XXXXXXXXXXXXXXXX",
        >>> )
        >>> buckets = s3_client.list_buckets()
        >>> print(buckets)
        """
        try:
            response = self.s3_client.list_buckets()
            return response['Buckets']
        except Exception as e:
            raise Exception(f"Error listing buckets: {e}")
        response = self.s3_client.list_buckets()
    

    def load(self, file_name: str| list[str] , prefix: str = ""):
        """
        Загрузка файла(ов) из S3.
        :param file_name: Имя файла или список имен файлов для загрузки.
        :param prefix: Префикс пути в бакете S3.
        :return: Словарь или список словарей с данными файлов.
        >>> {
        >>>     'Body': <botocore.response.StreamingBody>,
        >>>     'ContentLength': 125,
        >>>     'ContentType': 'application/json',
        >>>     'ETag': '"abc1234..."',
        >>>     'LastModified': datetime.datetime(2025, 10, 23, 8, 40, tzinfo=tzutc()),
        >>>     'Metadata': {
        >>>         'author': 'Stan',
        >>>         'version': '1'
        >>>     }
        >>> }
        :raises Exception: Если произошла ошибка при загрузке файла(ов).
        """
        if isinstance(file_name, list):
            keys = [f"{prefix}/{fn}" if prefix else fn for fn in file_name]
            responses = {}
            for key in keys:
                responses[key] = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return responses
        else:
            key = f"{prefix}/{file_name}" if prefix else file_name
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response
        
    def upload(
            self,
            file: FileStorage | list[FileStorage],
            prefix: str = ""):
        
        """
        Загрузка файла(ов) в S3.
        :param file: Объект werkzeug.FileStorage или объект(ы) совметимые с классом io.Base.
        :param prefix: Префикс пути в бакете S3.
        :return: None
        :raises Exception: Если произошла ошибка при загрузке файла(ов).
        """

        if isinstance(file, list):
            for f in file:
                key = f"{prefix}/{f.filename}" if prefix else f.filename
                self.s3_client.upload_fileobj(f, self.bucket_name, key)
        else:
            key = f"{prefix}/{file.filename}" if prefix else file.filename
            self.s3_client.upload_fileobj(file, self.bucket_name, key)
    
    def list(self, prefix: str = "") -> List[str]:
        """
        Получение списка файлов в бакете S3 с указанным префиксом.
        :param prefix: Префикс пути в бакете S3.
        :return: Список имен файлов.
        :raises Exception: Если произошла ошибка при получении списка файлов.
        """
        paginator = self.s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)

        keys = []
        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    keys.append(obj['Key'])
        return keys




if __name__ == "__main__":
    test_df  = LocalesModel()
    regions = test_df.get_regions()
    regions_index = [i for i in range(len(regions))]
    for region in regions:
        print(f"Region: {region}\t ID: {regions.index(region)}")  


