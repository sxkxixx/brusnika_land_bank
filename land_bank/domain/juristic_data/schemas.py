from uuid import UUID
from typing import List

from pydantic import BaseModel

__all__ = [
	'JuristicDataRelatedResponseDTO',
	'JuristicDataRequestDTO',
	'JuristicDataEditRequestDTO'
]


class _LimitPermittedUseRequestSchema(BaseModel):
	"""Схема созадния ограничения (обременения) и разрешенного пользования"""
	name: str


LimitRequestDTO = _LimitPermittedUseRequestSchema
PermittedUseRequestDTO = _LimitPermittedUseRequestSchema


class _LimitPermittedUseResponseSchema(_LimitPermittedUseRequestSchema):
	"""Схема ответа ограничения (обременения) и разрешенного пользования"""
	id: UUID


LimitResponseDTO = _LimitPermittedUseResponseSchema
PermittedUseResponseDTO = _LimitPermittedUseResponseSchema


class JuristicDataEditRequestDTO(BaseModel):
	buildings_count: int
	owners_count: int
	cadastral_cost: float
	limits: List['LimitResponseDTO']
	permitted_use_list: List['PermittedUseResponseDTO']


class JuristicDataRequestDTO(JuristicDataEditRequestDTO):
	"""Схема для созадния юридической информации"""
	land_area_id: UUID


class JuristicDataRelatedResponseDTO(JuristicDataRequestDTO):
	"""Схема ответа для юридической информации"""
	id: UUID
