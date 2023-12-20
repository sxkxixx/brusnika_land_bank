from datetime import datetime, timedelta
from typing import Dict

from infrastructure.database.model import Employee
from infrastructure.settings import AppSettings
from jose import jwt


class TokenService:
    def __init__(self, user: Employee):
        self.__user: Employee = user
        self.__data = {
            'email': user.email,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'department_id': user.department_id.__str__(),
        }

    @property
    def data(self) -> Dict:
        return self.__data

    def get_access_token(self) -> str:
        return self.__get_encode_token(
            ttl=timedelta(minutes=AppSettings.ACCESS_TOKEN_TTL_MINUTES))

    def __get_refresh_token(self) -> str:
        return self.__get_encode_token(
            ttl=timedelta(days=AppSettings.REFRESH_TOKEN_TTL_DAYS))

    def __get_encode_token(self, ttl: timedelta) -> str:
        data = self.__data.copy()
        expires_in = datetime.utcnow() + ttl
        data.update({'exp': expires_in, 'sub': 'access_token'})
        return jwt.encode(
            data,
            key=AppSettings.SECRET_KEY,
            algorithm=AppSettings.ALGORITHM
        )

    @staticmethod
    def get_token_payload(token: str) -> Dict:
        return jwt.decode(
            token,
            key=AppSettings.SECRET_KEY,
            algorithms=[AppSettings.ALGORITHM]
        )
