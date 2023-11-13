from pydantic import BaseModel


class TokenResponseSchema(BaseModel):
    access_token: str | None
    refresh_token_info: str = 'Set in Cookie'
