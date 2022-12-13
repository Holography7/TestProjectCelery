import datetime

from dependencies import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Header
from jose import JWTError
from odmantic.session import AIOSession
from settings import PWD_CONTEXT
from starlette import status

from todo_list.dependencies import credentials_exception, has_access
from todo_list.enums import TokenEnum
from todo_list.models import TODOList, User
from todo_list.schemes.request import (
    RefreshTokenRequestScheme,
    TODOListRequestScheme,
    UserLoginRequestScheme,
    UserRegistrationRequestScheme,
)
from todo_list.schemes.response import (
    TODOListResponseScheme,
    TokensPairScheme,
    UserResponseScheme,
)
from todo_list.utils import create_token, decode_token

router = APIRouter()


@router.post(
    '/tokens',
    response_model=TokensPairScheme,
    status_code=status.HTTP_201_CREATED,
)
async def create_tokens(
        user_data: UserLoginRequestScheme,
        db_session: AIOSession = Depends(get_db_session),
) -> dict:
    user = await db_session.find_one(
        User,
        User.username == user_data.username,
    )
    if not user:
        raise HTTPException(status_code=401, detail='Bad username or password')
    password_is_correct = PWD_CONTEXT.verify(user_data.password, user.password)
    if not password_is_correct:
        raise HTTPException(status_code=401, detail='Bad username or password')
    access_token = create_token(user_data.username)
    refresh_token = create_token(
        user_data.username,
        token_type=TokenEnum.REFRESH,
    )
    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.post(
    '/tokens/refresh',
    response_model=TokensPairScheme,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_tokens(
        token: RefreshTokenRequestScheme,
        db_session: AIOSession = Depends(get_db_session),
) -> dict:
    try:
        payload = decode_token(token.refresh_token, TokenEnum.REFRESH)
    except JWTError:
        raise credentials_exception
    username = payload.get('sub')
    if username is None:
        raise credentials_exception
    user = await db_session.find_one(User, User.username == username)
    if user is None:
        raise credentials_exception
    access_token = create_token(user.username)
    refresh_token = create_token(user.username, token_type=TokenEnum.REFRESH)
    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.get('/profile', response_model=UserResponseScheme)
async def profile(user: User = Depends(has_access)) -> User:
    return user


@router.post(
    '/registration',
    response_model=UserResponseScheme,
    status_code=status.HTTP_201_CREATED,
)
async def registration(
        user_creds: UserRegistrationRequestScheme,
        authorization: str | None = Header(default=None),
        db_session: AIOSession = Depends(get_db_session),
) -> UserRegistrationRequestScheme:
    if authorization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Registration not allowed for registered users',
        )
    hashed_pass = PWD_CONTEXT.hash(user_creds.password)
    user = User(
        username=user_creds.username,
        password=hashed_pass,
        telegram=user_creds.telegram,
        last_seen=datetime.datetime.now(),
    )
    await db_session.save(user)
    return user_creds


@router.post(
    '/todo_list/create',
    response_model=TODOListResponseScheme,
    status_code=status.HTTP_201_CREATED,
)
async def create_todo_list(
        todo_list_data: TODOListRequestScheme,
        user: User = Depends(has_access),
        db_session: AIOSession = Depends(get_db_session),
) -> TODOList:
    todo_list = TODOList(name=todo_list_data.name, user=user)
    await db_session.save(todo_list)
    return todo_list


@router.get('/todo_list', response_model=list[TODOListResponseScheme])
async def get_todo_lists(
        user: User = Depends(has_access),
        db_session: AIOSession = Depends(get_db_session),
) -> list[TODOList]:
    if user.is_superuser:
        return await db_session.find(TODOList)
    else:
        return await db_session.find(TODOList, TODOList.user == user.id)
