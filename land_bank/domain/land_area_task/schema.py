from pydantic import BaseModel, field_validator, Field
from domain.employee.schema import ShortEmployeeResponseDTO
from domain.land_area.schema import ShortLandAreaResponseDTO
from typing import Optional
from uuid import UUID
from datetime import datetime

__all__ = [
	'TaskRequestDTO',
	'TaskRelatedResponseDTO',
	'ListTaskResponseDTO',
	'EditTaskRequestDTO'
]


class TaskRequestDTO(BaseModel):
	name: str = Field(
		..., description='Not nullable', max_length=64)
	description: Optional[str] = Field(
		None, description='Nullable')
	executor_id: UUID
	land_area_id: UUID
	started_at: Optional[datetime] = None
	deadline: datetime

	@field_validator('description')
	@classmethod
	def validate_description_length(cls, field: str) -> str:
		if not field:
			return field
		if len(field) > 128:
			raise ValueError('Field "description" must be lte 128 symbols')
		return field


class EditTaskRequestDTO(TaskRequestDTO):
	status: str


class TaskRelatedResponseDTO(TaskRequestDTO):
	status: str
	executor: 'ShortEmployeeResponseDTO'
	author_id: UUID
	author: 'ShortEmployeeResponseDTO'
	land_area: 'ShortLandAreaResponseDTO'


class ListTaskResponseDTO(BaseModel):
	id: UUID
	name: str
	status: str
	land_area_id: UUID
	land_area: 'ShortLandAreaResponseDTO'
	deadline: datetime
