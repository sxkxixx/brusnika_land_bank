from domain.employee.schema import ShortEmployeeResponseDTO
from pydantic import BaseModel, EmailStr, Field, field_validator
from domain.extra_data.schemas import ExtraDataResponseSchema
from typing import Optional, List, Union
from datetime import datetime
from uuid import UUID
import re

__all__ = [
	'OwnerRequestDTO',
	'LandAreaRequestDTO',
	'BuildingRequestDTO',
	'LandAreaRelatedResponseDTO',
	'LandAreaListResponseDTO',
	'ShortLandAreaResponseDTO',
	'LandAreaResponseDTO',
	'BuildingResponseDTO',
	'OwnerResponseDTO'
]


def _phone_number_validator(field: Union[str, None]) -> Union[str, None]:
	if field is None:
		return field
	if re.match('^\\+?[1-9][0-9]{7,14}$', field) is None:
		raise ValueError('Incorrect Phone Number')
	return field


class _InternalAreaCommentModel(BaseModel):
	id: UUID
	comment_text: str
	land_area_id: UUID
	employee_id: UUID
	created_at: datetime
	employee: 'ShortEmployeeResponseDTO'


class OwnerRequestDTO(BaseModel):
	name: Optional[str] = None
	email: Optional[EmailStr] = None
	phone_number: str
	location: Optional[str] = None

	@field_validator('phone_number')
	@classmethod
	def validate_phone_number(cls, field: str):
		return _phone_number_validator(field)


class OwnerResponseDTO(OwnerRequestDTO):
	id: UUID
	land_area_id: UUID


class BuildingRequestDTO(BaseModel):
	name: str
	description: Optional[str] = None
	commissioning_year: Optional[int] = None


class BuildingResponseDTO(BuildingRequestDTO):
	id: UUID
	land_area_id: UUID


class ShortLandAreaResponseDTO(BaseModel):
	id: UUID
	name: str
	cadastral_number: str


class LandAreaRequestDTO(BaseModel):
	name: str
	cadastral_number: str
	area_category: str
	cadastral_cost: Optional[float] = None
	area_square: float
	address: Optional[str]
	search_channel: str
	working_status: str = Field('Новый')
	stage: str = Field('Поиск')

	@field_validator('cadastral_cost')
	@classmethod
	def validate_positive_cost(cls, field: Optional[float]) -> float | None:
		if field is None:
			return field
		if field <= 0:
			raise ValueError('"cadastral_cost" must be gt 0.0')
		return field

	@field_validator('cadastral_number')
	@classmethod
	def cadastral_number_validator(cls, field: str) -> str:
		if re.match(
				"[0-9]{2}:[0-9]{2}:[0-9]{6,7}:[0-9]{1,6}", field
		) is None:
			raise ValueError('"cadastral_number" is invalid')
		return field

	@field_validator('area_square')
	@classmethod
	def positive_number_validator(cls, field: float) -> float:
		if field <= 0:
			raise ValueError(
				'"area_square" can\'t be less than 0')
		return field


class LandAreaResponseDTO(LandAreaRequestDTO):
	id: UUID
	entered_at_base: datetime
	working_status: str
	stage: str


class LandAreaRelatedResponseDTO(LandAreaResponseDTO):
	area_buildings: Optional[List['BuildingResponseDTO']] = None
	owners: Optional[List['OwnerResponseDTO']] = None
	comments: Optional[List['_InternalAreaCommentModel']] = None
	extra_data: Optional['ExtraDataResponseSchema'] = None


class LandAreaListResponseDTO(BaseModel):
	id: UUID
	name: str
	cadastral_number: str
	area_category: str
	area_square: float
	entered_at_base: datetime
	working_status: str
	stage: str
	owners: List['OwnerResponseDTO']
