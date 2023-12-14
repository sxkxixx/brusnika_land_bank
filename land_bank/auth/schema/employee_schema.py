import re
from typing import Optional, Union
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    model_validator,
    field_validator,
)

__all__ = [
    'EmployeeLoginSchema',
    'EmployeeCreateSchema',
    'EmployeeReadSchema',
    'EmployeeRelationsResponse',
    'DepartmentReadSchema',
    'PositionReadSchema'
]


class EmployeeLoginSchema(BaseModel):
    email: EmailStr
    password: str


class EmployeeCreateSchema(EmployeeLoginSchema):
    password_repeat: str
    last_name: str
    first_name: str
    patronymic: Optional[str] = None
    phone_number: Optional[str] = None

    @model_validator(mode='after')
    def validate_passwords(self):
        if self.password != self.password_repeat:
            raise ValueError('Passwords don\'t match')
        return self

    @field_validator('password', 'password_repeat', mode='after')
    @classmethod
    def validate_password_length(cls, field: str) -> str:
        if len(field) < 12:
            raise ValueError(
                f'Password must be at least 12 symbols'
            )
        return field

    @field_validator('phone_number', mode='after')
    @classmethod
    def validate_phone_number(cls, field: Union[str | None]):
        if field is None:
            return field
        if re.match('^\\+?[1-9][0-9]{7,14}$', field) is None:
            raise ValueError('Incorrect Phone Number')
        return field

    @field_validator('email', mode='after')
    @classmethod
    def email_to_lower(cls, field: str) -> str:
        return field.lower()

    @field_validator(
        'last_name',
        'first_name',
        'patronymic',
        mode='after'
    )
    @classmethod
    def capitalize(cls, field: Union[str | None]):
        if field is None:
            return field
        return field.capitalize()


class EmployeeReadSchema(BaseModel):
    id: UUID
    email: EmailStr
    last_name: str
    first_name: str
    patronymic: Optional[str] = None
    phone_number: Optional[str] = None
    s3_avatar_file: Optional[str] = None
    position_id: Optional[int] = None
    department_id: Optional[UUID] = None


class PositionReadSchema(BaseModel):
    id: int
    position_name: str
    is_director_position: bool


class DepartmentReadSchema(BaseModel):
    id: UUID
    department_name: str


class EmployeeRelationsResponse(EmployeeReadSchema):
    employee_head: Optional[EmployeeReadSchema] = None
    position: Optional['PositionReadSchema'] = None
    department: Optional['DepartmentReadSchema'] = None

    @classmethod
    def from_model(cls, model):
        return cls.model_validate(model, from_attributes=True)
