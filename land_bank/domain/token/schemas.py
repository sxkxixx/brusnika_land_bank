from pydantic import BaseModel

__all__ = [
	'TokenResponseSchema'
]


class TokenResponseSchema(BaseModel):
	access_token: str | None
