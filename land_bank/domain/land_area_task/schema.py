from pydantic import BaseModel, field_validator, Field
from domain.employee.schema import ShortEmployeeResponseDTO
from domain.land_area.schema import ShortLandAreaResponseDTO
from typing import Optional
from uuid import UUID
from datetime import datetime

__all__ = [
	'TaskRequestDTO',
	'TaskRelatedResponseDTO',
	'EditTaskRequestDTO',
	'TaskListResponseDTO',
	'SchedulerTaskResponseDTO',
	'TaskResponseDTO'
]


class TaskRequestDTO(BaseModel):
	"""
	Схема для создания задачи для земельного участка
	"""
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
	"""
	Схема для обновление полей задачи
	"""
	status: str


class TaskResponseDTO(TaskRequestDTO):
	id: UUID
	author_id: UUID
	status: str


class TaskRelatedResponseDTO(TaskResponseDTO):
	"""
	Схема для вывода полной информации по задаче с отношениями
	"""
	executor: 'ShortEmployeeResponseDTO'
	author: 'ShortEmployeeResponseDTO'
	land_area: 'ShortLandAreaResponseDTO'


class SchedulerTaskResponseDTO(TaskResponseDTO):
	"""
	Схема для вывода информации по задаче в планировщике задач
	"""
	land_area: 'ShortLandAreaResponseDTO'


class TaskListResponseDTO(TaskResponseDTO):
	"""
	Схема для вывода информации по задаче в списке задач земельного участка
	"""
	executor: 'ShortEmployeeResponseDTO'
