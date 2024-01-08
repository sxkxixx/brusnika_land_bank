from uuid import UUID
from typing import List

from pydantic import BaseModel

__all__ = [
	'LimitSchema',
	'PermittedUseSchema',
	'JuristicDataResponseDTO'
]


class _LimitPermittedUseResponseSchema(BaseModel):
	"""Схема ответа ограничения (обременения) и разрешенного пользования"""
	name: str
	id: UUID


LimitSchema = _LimitPermittedUseResponseSchema
PermittedUseSchema = _LimitPermittedUseResponseSchema


class JuristicDataResponseDTO(BaseModel):
	limits: List[_LimitPermittedUseResponseSchema]
	permitted_uses: List[_LimitPermittedUseResponseSchema]
