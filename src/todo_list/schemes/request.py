from pydantic import BaseModel, Field, root_validator, validator


class UserRegistrationRequestScheme(BaseModel):
    username: str
    password: str = Field(min_length=10)
    repeat_password: str = Field(min_length=10)
    telegram: str = Field(max_length=33)

    @validator('telegram')
    def check_telegram(cls, value: str) -> str:
        if not value.startswith('@'):
            raise ValueError('telegram must starts with @ symbol')
        return value

    @root_validator(pre=True)
    def passwords_match(cls, values: dict) -> dict:
        if values['password'] != values['repeat_password']:
            raise ValueError('passwords do not match')
        return values


class UserLoginRequestScheme(BaseModel):
    username: str
    password: str


class RefreshTokenRequestScheme(BaseModel):
    refresh_token: str


class TODOListRequestScheme(BaseModel):
    name: str
