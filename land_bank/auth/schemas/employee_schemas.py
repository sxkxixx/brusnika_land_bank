import re
from typing import Optional, Union

from pydantic import (
    BaseModel,
    EmailStr,
    model_validator,
    field_validator,
)

__all__ = [
    'EmployeeLoginSchema',
    'EmployeeCreateSchema',
    'EmployeeReadSchema'
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
    tg_username: str

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

    @field_validator('tg_username', mode='after')
    @classmethod
    def validate_tg_username(cls, field: str):
        if not field.startswith('@'):
            raise ValueError(
                f'Telegram username must starts with "@"'
            )
        return field


class EmployeeReadSchema(BaseModel):
    email: EmailStr
    last_name: str
    first_name: str
    patronymic: Optional[str] = None
    phone_number: Optional[str] = None
    tg_username: str

    @classmethod
    def from_model(cls, model):
        return cls(
            email=model.email,
            last_name=model.last_name,
            first_name=model.first_name,
            patronymic=model.patronymic,
            phone_number=model.phone_number,
            tg_username=model.tg_username,
        )

