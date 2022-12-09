import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from settings import MONGO_ENGINE, PWD_CONTEXT

from todo_list.dependencies import has_access
from todo_list.enums import TokenEnum
from todo_list.models import User
from todo_list.schemes.request import (
    RefreshTokenRequestScheme,
    UserLoginRequestScheme,
    UserRegistrationRequestScheme,
)
from todo_list.schemes.response import TokensPairScheme, UserResponseScheme
from todo_list.utils import create_token

router = APIRouter()
auth_dependence = Depends(has_access)


@router.post('/tokens', response_model=TokensPairScheme)
async def create_tokens(user_data: UserLoginRequestScheme) -> dict:
    user = await MONGO_ENGINE.find_one(
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


@router.post('/tokens/refresh', response_model=TokensPairScheme)
async def refresh_tokens(token: RefreshTokenRequestScheme) -> dict:
    user = await has_access(
        HTTPAuthorizationCredentials(
            scheme='Bearer',
            credentials=token.refresh_token,
        ),
        TokenEnum.REFRESH,
    )
    access_token = create_token(user.username)
    refresh_token = create_token(user.username, token_type=TokenEnum.REFRESH)
    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.get('/profile', response_model=UserResponseScheme)
async def profile(user: User = auth_dependence) -> User:
    return user


@router.post('/registration', response_model=UserResponseScheme)
async def registration(
        user_creds: UserRegistrationRequestScheme,
) -> UserRegistrationRequestScheme:
    hashed_pass = PWD_CONTEXT.hash(user_creds.password)
    user = User(
        username=user_creds.username,
        password=hashed_pass,
        telegram=user_creds.telegram,
        last_seen=datetime.datetime.now(),
    )
    await MONGO_ENGINE.save(user)
    return user_creds
