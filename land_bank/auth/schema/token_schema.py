from pydantic import BaseModel


class TokenResponseSchema(BaseModel):
    access_token: str | None

