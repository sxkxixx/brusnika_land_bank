from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

from domain.employee import ShortEmployeeResponseDTO


class AreaCommentRequestDTO(BaseModel):
    comment_text: str
    land_area_id: UUID

    @field_validator('comment_text')
    @classmethod
    def validate_comment_text_length(cls, field: str):
        if len(field) > 128:
            raise ValueError('Comment text must be lte of 128 chars')
        return field


class AreaCommentResponseDTO(AreaCommentRequestDTO):
    id: UUID
    employee_id: UUID
    created_at: datetime


class AreaCommentRelatedResponseDTO(AreaCommentResponseDTO):
    employee: 'ShortEmployeeResponseDTO'
