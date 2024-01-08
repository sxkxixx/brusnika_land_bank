from datetime import timedelta
from typing import Optional, Type, Union
from uuid import uuid4

import aioredis
from infrastructure.settings import RedisSettings
from abc import ABC, abstractmethod

redis = aioredis.Redis(
	host=RedisSettings.REDIS_HOST,
	port=RedisSettings.REDIS_PORT,
)


class RedisObject(ABC):
	@classmethod
	@abstractmethod
	def from_json_string(cls, string: str) -> 'RedisObject':
		raise NotImplementedError()

	@abstractmethod
	def to_json_string(self) -> str:
		raise NotImplementedError()

	@abstractmethod
	def time_to_leave(self) -> timedelta:
		raise NotImplementedError()


class RedisService:
	@staticmethod
	async def setex_entity(entity: 'RedisObject') -> str:
		"""
		Создает запись питоновского объекта в редисе и возвращает ключ записи
		:param entity: Модель данных для отправки в redis
		:return: Ключ записи в redis
		"""
		json_string = entity.to_json_string()
		key = str(uuid4())
		await redis.setex(
			name=key, time=entity.time_to_leave(), value=json_string
		)
		return key

	@staticmethod
	async def delete_by_key(key: str) -> None:
		"""
		Удаляет объект из Redis по ключу
		:param key: Ключ
		:return: None
		"""

		return await redis.delete(key)

	@staticmethod
	async def get_by_key(
			key: str,
			_class: Type['RedisObject']
	) -> Optional['RedisObject']:
		"""
		Достает и возвращает объект из редиса или None, если объект отсутствует
		:param key: Ключ
		:param _class: Класс, к которому необходимо преобразовать json-строку
		:return: _class | None
		"""
		json_encoded: str = await redis.get(key)
		if not json_encoded:
			return None
		return _class.from_json_string(json_encoded)
