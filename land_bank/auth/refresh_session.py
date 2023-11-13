import json
from datetime import timedelta
from uuid import uuid4, UUID
from typing import Union

from core import get_redis, Config
from core.rpc_exceptions import AuthorizationError


class RefreshSession:
    redis = get_redis(0)

    def __init__(
            self,
            user_id: Union[str, UUID],
            user_agent: str
    ):
        self.__user_id = user_id
        self.__user_agent = user_agent

    @property
    def user_agent(self):
        return self.__user_agent

    @property
    def user_id(self):
        return self.__user_id

    def __data_str(self) -> str:
        return json.dumps(
            {
                'user_id': self.__user_id,
                'user_agent': self.__user_agent
            },
            default=str
        )

    async def delete(self, key: str):
        await self.redis.delete(key)

    @staticmethod
    def __from_str(encoded_data: str) -> dict:
        return json.loads(encoded_data)

    @classmethod
    async def get_by_key(cls, key: str) -> 'RefreshSession':
        encoded_data = await cls.redis.get(key)
        if encoded_data is None:
            raise AuthorizationError(data='Session has expired, login again')
        data = cls.__from_str(encoded_data)
        return cls(**data)

    async def push(self) -> str:
        encoded_data = self.__data_str()
        key = str(uuid4())
        await self.redis.setex(
            name=key,
            time=timedelta(days=Config.REFRESH_TOKEN_TTL_DAYS),
            value=encoded_data
        )
        return key
