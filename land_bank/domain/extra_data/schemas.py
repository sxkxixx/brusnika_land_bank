from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

__all__ = [
    'ExtraDataEditSchema',
    'ExtraDataRequestSchema',
    'ExtraDataResponseSchema'
]


class ExtraDataEditSchema(BaseModel):
    engineering_networks: Optional[str] = Field(None, max_length=128)
    transport: Optional[str] = Field(None, max_length=128)
    result: Optional[str] = Field(None, max_length=256)


class ExtraDataRequestSchema(ExtraDataEditSchema):
    land_area_id: UUID


class ExtraDataResponseSchema(ExtraDataRequestSchema):
    id: UUID
