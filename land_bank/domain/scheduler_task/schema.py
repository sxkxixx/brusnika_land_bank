from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, field_validator, Field

from domain.employee.schema import ShortEmployeeResponseDTO
from domain.land_area.schema import ShortLandAreaResponseDTO

__all__ = [
    'TaskRequestDTO',
    'TaskRelatedResponseDTO',
    'TaskListResponseDTO',
    'SchedulerTaskResponseDTO',
    'TaskResponseDTO',
    'TaskEditRequestDTO'
]

from domain.task_comment.schema import TaskCommentRelatedRequestDTO


class TaskEditRequestDTO(BaseModel):
    name: str = Field(
        ..., description='Not nullable', max_length=64)
    description: Optional[str] = Field(
        None, description='Nullable')
    executor_id: UUID
    started_at: datetime
    deadline: datetime
    status: str = 'Создана'


class TaskRequestDTO(TaskEditRequestDTO):
    """
    Схема для создания задачи для земельного участка
    """
    executor_id: UUID
    land_area_id: UUID

    @field_validator('description')
    @classmethod
    def validate_description_length(cls, field: str) -> str:
        if not field:
            return field
        if len(field) > 128:
            raise ValueError('Field "description" must be lte 128 symbols')
        return field


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

    task_comments: List['TaskCommentRelatedRequestDTO']


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
