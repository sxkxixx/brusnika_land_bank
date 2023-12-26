from domain.employee.schema import ShortEmployeeResponseDTO
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re

__all__ = [
	'OwnerRequestDTO',
	'LandAreaRequestDTO',
	'BuildingRequestDTO',
	'LandAreaRelatedResponseDTO',
	'LandAreaListResponseDTO',
	'StageResponseDTO',
	'StatusResponseDTO',
	'ShortLandAreaResponseDTO',
	'LandAreaResponseDTO'
]


class _InternalAreaCommentModel(BaseModel):
	id: UUID
	employee_id: UUID
	created_at: datetime
	employee: 'ShortEmployeeResponseDTO'


class StageResponseDTO(BaseModel):
	id: UUID
	stage_name: str


class StatusResponseDTO(BaseModel):
	id: UUID
	status_name: str


class OwnerRequestDTO(BaseModel):
	name: Optional[str] = None
	email: Optional[EmailStr] = None
	phone_number: str
	location: Optional[str] = None


class OwnerResponseDTO(OwnerRequestDTO):
	id: UUID
	land_area_id: UUID


class BuildingRequestDTO(BaseModel):
	name: str
	description: Optional[str] = None
	commissioning_year: str


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
	area_square: float
	address: Optional[str]
	search_channel: str

	@field_validator('cadastral_number')
	@classmethod
	def cadastral_number_validator(cls, field: str) -> str:
		if re.match("[0-9]{2}:[0-9]{2}:[0-9]{6,7}:[0-9]{1,6}", field):
			return field
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
	working_status_id: UUID
	stage_id: UUID


class LandAreaRelatedResponseDTO(LandAreaResponseDTO):
	stage: 'StageResponseDTO'
	status: 'StatusResponseDTO'
	area_buildings: Optional[List['BuildingResponseDTO']] = None
	owners: Optional[List['OwnerResponseDTO']] = None
	comments: Optional[List['_InternalAreaCommentModel']] = None


class LandAreaListResponseDTO(BaseModel):
	id: UUID
	name: str
	cadastral_number: str
	area_category: str
	area_square: float
	entered_at_base: datetime
	status: 'StatusResponseDTO'
	stage: 'StageResponseDTO'
	owners: List['OwnerResponseDTO']
