from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from settings import (
    JWT_ACCESS_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_REFRESH_SECRET_KEY,
    MONGO_ENGINE,
)
from starlette import status

from todo_list.enums import TokenEnum
from todo_list.models import User

security = Depends(HTTPBearer())
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Invalid or expired token',
    headers={'Authenticate': 'Bearer'},
)


async def has_access(
        credentials: HTTPAuthorizationCredentials = security,
        token_type: TokenEnum = TokenEnum.ACCESS,
) -> User:
    token = credentials.credentials
    secret_key = (
        JWT_ACCESS_SECRET_KEY
        if token_type == TokenEnum.ACCESS
        else JWT_REFRESH_SECRET_KEY
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise credentials_exception
    username = payload.get('sub')
    if username is None:
        raise credentials_exception
    user = await MONGO_ENGINE.find_one(User, User.username == username)
    if user is None:
        raise credentials_exception
    return user
