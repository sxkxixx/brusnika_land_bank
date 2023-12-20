from typing import List, Optional, Literal

from pydantic import BaseModel, field_validator


class SortParams(BaseModel):
    fields: Optional[List[str]] = None
    order: Optional[Literal['asc', 'desc']] = None

    @field_validator('order')
    @classmethod
    def validate_order(cls, field: str) -> str:
        if field in ['asc', 'desc']:
            return field
        raise ValueError('Field "order" must "asc" or "desc"')


class LimitOffset(BaseModel):
    offset: int = 0
    limit: int = 20

    @field_validator('offset', 'limit')
    @classmethod
    def validate(cls, field: int) -> int:
        if field < 0:
            raise ValueError('Fields "offset" & "limit" must be gte 0')
        return field