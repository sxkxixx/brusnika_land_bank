from pydantic import BaseModel, EmailStr

__all__ = [
    'PasswordResetRequestDTO',
    'PasswordResetResponseDTO'
]


class PasswordResetRequestDTO(BaseModel):
    email: EmailStr


class PasswordResetResponseDTO(PasswordResetRequestDTO):
    status: str = 'Message sent to email'
