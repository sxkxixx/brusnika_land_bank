from datetime import datetime, timedelta
from typing import Dict

from .models import Employee
from core import Config
from jose import jwt


class TokenService:
    def __init__(self, user: Employee):
        self.__user: Employee = user
        self.__data = {
            'email': user.email,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'dp_id': user.department_id.__str__(),
        }

    @property
    def data(self) -> Dict:
        return self.__data

    def get_access_token(self) -> str:
        return self.__get_encode_token(
            ttl=timedelta(minutes=Config.ACCESS_TOKEN_TTL_MINUTES))

    def __get_refresh_token(self) -> str:
        return self.__get_encode_token(
            ttl=timedelta(days=Config.REFRESH_TOKEN_TTL_DAYS))

    def __get_encode_token(self, ttl: timedelta) -> str:
        data = self.__data.copy()
        expires_in = datetime.now() + ttl
        data.update({'expires_in': expires_in})
        return jwt.encode(
            data,
            key=Config.SECRET_KEY,
            algorithm=Config.ALGORITHM
        )

    @staticmethod
    def get_token_payload(token: str) -> Dict:
        return jwt.decode(
            token,
            key=Config.SECRET_KEY,
            algorithms=[Config.ALGORITHM]
        )
