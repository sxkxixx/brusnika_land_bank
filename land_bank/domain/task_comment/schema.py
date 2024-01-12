from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

from domain.employee import ShortEmployeeResponseDTO


class TaskCommentRequestDTO(BaseModel):
    task_id: UUID
    text: str

    @field_validator('text')
    @classmethod
    def validate_text_length(cls, field: str) -> str:
        if len(field) > 128:
            raise ValueError('Comment text must be lte 128 characters')
        return field


class TaskCommentResponseDTO(TaskCommentRequestDTO):
    id: UUID
    employee_id: UUID
    created_at: datetime


class TaskCommentRelatedRequestDTO(TaskCommentResponseDTO):
    employee: 'ShortEmployeeResponseDTO'
