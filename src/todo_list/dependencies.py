from dependencies import get_db_session
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from odmantic.session import AIOSession
from starlette import status

from todo_list.enums import TokenEnum
from todo_list.models import User
from todo_list.utils import decode_token

security = Depends(HTTPBearer())
credentials_exception = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    'Invalid or expired token',
    {'Authenticate': 'Bearer'},
)


async def has_access(
        credentials: HTTPAuthorizationCredentials = security,
        db_session: AIOSession = Depends(get_db_session),  # noqa
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token, TokenEnum.ACCESS)
    except JWTError:
        raise credentials_exception
    username = payload.get('sub')
    if username is None:
        raise credentials_exception
    user = await db_session.find_one(User, User.username == username)
    if user is None:
        raise credentials_exception
    return user
