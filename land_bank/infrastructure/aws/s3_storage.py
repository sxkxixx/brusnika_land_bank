import os

import aioboto3
from fastapi import File, UploadFile

from infrastructure.settings import S3Settings


class S3Storage:
    __service_name = 's3'
    __session = aioboto3.Session(
        aws_access_key_id=S3Settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=S3Settings.AWS_SECRET_ACCESS_KEY,
        region_name=S3Settings.REGION_NAME,
    )

    async def upload_file(self, file: UploadFile = File(...)) -> str:
        """
        Загружает файл в s3 хранилище и возвращает его уникальные название
        :param file: Загружаемый файл
        :return: Уникальное название загруженного файла
        """
        async with self.__session.client(
                self.__service_name,
                endpoint_url=S3Settings.S3_ENDPOINT_URL
        ) as client:
            file_name = self.__get_unique_file_name(file.filename)
            await client.upload_fileobj(
                file,
                S3Settings.BUCKET_NAME,
                file_name
            )
        return file_name

    async def get_pre_signed_url(self, file_name) -> str:
        """
        Возвращает ссылку на файл из s3 хранилища
        :param file_name: Название файла
        :return: Ссылка в строковом виде
        """
        async with self.__session.client(
                self.__service_name,
                endpoint_url=S3Settings.S3_ENDPOINT_URL
        ) as client:
            url = await client.generate_presigned_url(
                'get_object',
                Params={"Bucket": S3Settings.BUCKET_NAME, "Key": file_name},
                ExpiresIn=3600
            )
        return url

    async def delete_file(self, file_name):
        """
        Удаляет файл из s3 хранилища
        :param file_name: Название файла
        :return:
        """
        async with self.__session.client(
                self.__service_name,
                endpoint_url=S3Settings.S3_ENDPOINT_URL
        ) as client:
            response = await client.delete_object(
                Bucket=S3Settings.BUCKET_NAME,
                Key=file_name
            )
        return response

    def __get_unique_file_name(self, filename: str) -> str:
        """
        Возвращает рандомное название файла
        :param filename: Исходное название файла
        :return: Рандомное название файла
        """
        return os.urandom(8).hex() + filename[filename.rfind('.'):]