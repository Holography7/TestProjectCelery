from uuid import UUID

from pydantic import BaseModel


class UserResponseScheme(BaseModel):
    username: str
    telegram: str


class TokensPairScheme(BaseModel):
    access_token: str
    refresh_token: str


class TODOListResponseScheme(BaseModel):
    uuid: UUID
    name: str
