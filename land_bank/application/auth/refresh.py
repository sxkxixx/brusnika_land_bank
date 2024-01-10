import json
from datetime import timedelta
from typing import Union
from uuid import UUID

from infrastructure.redis import RedisObject
from infrastructure.settings import AppSettings


class RefreshSession(RedisObject):
    def __init__(
            self,
            user_id: Union[str, UUID],
            user_agent: str
    ):
        self.__user_id = user_id
        self.__user_agent = user_agent

    def to_json_string(self) -> str:
        return json.dumps(
            {
                'user_id': self.__user_id,
                'user_agent': self.__user_agent
            },
            default=str
        )

    @classmethod
    def from_json_string(cls, string: str) -> 'RefreshSession':
        data = json.loads(string)
        return RefreshSession(
            user_id=data.get('user_id'),
            user_agent=data.get('user_agent')
        )

    def time_to_leave(self) -> timedelta:
        return timedelta(days=AppSettings.REFRESH_TOKEN_TTL_DAYS)

    @property
    def user_agent(self):
        return self.__user_agent

    @property
    def user_id(self):
        return self.__user_id
