import datetime

from dependencies import get_db_session
from fastapi import Depends
from jose import jwt
from odmantic import query
from odmantic.session import AIOSession
from pymongo.errors import ConnectionFailure
from settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ACCESS_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_REFRESH_SECRET_KEY,
)

from todo_list.enums import TokenEnum
from todo_list.models import User


async def check_database(
        db_session: AIOSession = Depends(get_db_session),  # noqa
) -> dict:
    try:
        await db_session.find_one(User, query.eq(User.is_superuser, True))
    except ConnectionFailure as exc:
        status = {'Database': str(exc)}
    else:
        status = {'Database': 'OK'}
    return status


def create_token(
        username: str,
        expires_delta: datetime.timedelta | None = None,
        token_type: TokenEnum = TokenEnum.ACCESS,
) -> str:
    expire = datetime.datetime.utcnow() + (
        expires_delta or datetime.timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    )
    claims = {'sub': username, 'exp': expire, 'type': token_type.value}
    secret_key = (
        JWT_ACCESS_SECRET_KEY
        if token_type == TokenEnum.ACCESS
        else JWT_REFRESH_SECRET_KEY
    )
    encoded_jwt = jwt.encode(
        claims,
        secret_key,
        algorithm=JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str, token_type: TokenEnum = TokenEnum.ACCESS) -> dict:
    secret_key = (
        JWT_ACCESS_SECRET_KEY
        if token_type == TokenEnum.ACCESS
        else JWT_REFRESH_SECRET_KEY
    )
    return jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
