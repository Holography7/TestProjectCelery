import datetime
from uuid import UUID

from bson import Binary
from celery_app.tasks import (
    delete_user_after_inactive_period,
    send_message_about_deleting,
)
from dependencies import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Header
from jose import JWTError
from odmantic.session import AIOSession
from settings import COUNT_DAYS_TO_DELETE_USER_AFTER_INACTIVE as INACTIVE_DAYS
from settings import PWD_CONTEXT
from starlette import status

from todo_list.dependencies import (
    credentials_exception,
    get_todo_list_by_uuid,
    has_access,
)
from todo_list.enums import TokenEnum
from todo_list.flake8_fastapi_fix import fix_cf009
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
    )
    await db_session.save(user)
    task_result = delete_user_after_inactive_period.apply_async(
        (user_creds.username,),
        eta=datetime.datetime.utcnow() + datetime.timedelta(days=INACTIVE_DAYS)
    )
    user.celery_task_id = Binary.from_uuid(UUID(task_result.id))
    await db_session.save(user)
    return user_creds


@router.post(
    '/todo_list',
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


@router.get('/todo_list/{uuid}', response_model=TODOListResponseScheme)
async def get_todo_list(
        uuid: UUID,
        dependencies: tuple[User, TODOList, AIOSession] = Depends(
            get_todo_list_by_uuid,
        ),
) -> TODOList:
    return dependencies[1]


@router.put('/todo_list/{uuid}', response_model=TODOListResponseScheme)
async def update_todo_list(
        uuid: UUID,
        todo_list_data: TODOListRequestScheme,
        dependencies: tuple[User, TODOList, AIOSession] = Depends(
            get_todo_list_by_uuid,
        ),
) -> TODOList:
    todo_list, db_session = dependencies[1], dependencies[2]
    # todo_list.update(todo_list_data) crush pre-commit hook flake8. It causes
    # by flake8-fastapi plugin that cannot find 'update' function declaration.
    # noqa doesn't help in this case, but if declare 'fix_cf009' function and
    # save returned value to 'fixed' it works somehow, but it causes mypy check
    # error, so this string marked as ignore for him. I hope flake8-fastapi
    # plugin will fix soon.
    # issue: https://github.com/Kludex/flake8-fastapi/issues/28
    fixed = fix_cf009(todo_list.update(todo_list_data))  # type: ignore
    if not fixed:
        raise ValueError("'Fix for CF009 doesn't work")
    await db_session.save(todo_list)
    return todo_list


@router.delete('/todo_list/{uuid}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_list(
        uuid: UUID,
        dependencies: tuple[User, TODOList, AIOSession] = Depends(
            get_todo_list_by_uuid,
        ),
) -> None:
    user, todo_list, db_session = dependencies
    await db_session.delete(todo_list)
    if user.is_superuser and user.id != todo_list.user:
        telegrams = [
            other_user.telegram
            async for other_user in db_session.find(
                User,
                User.id != todo_list.user.id,
            )
        ]
        for telegram in telegrams:
            send_message_about_deleting.delay(
                todo_list.user.username,
                todo_list.name,
                telegram,
            )
