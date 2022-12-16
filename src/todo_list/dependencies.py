import datetime
from uuid import UUID

from bson import Binary
from celery.result import AsyncResult
from celery_app.tasks import delete_user_after_inactive_period
from dependencies import get_db_session
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from odmantic.session import AIOSession
from settings import COUNT_DAYS_TO_DELETE_USER_AFTER_INACTIVE as INACTIVE_DAYS
from starlette import status

from todo_list.enums import TokenEnum
from todo_list.models import TODOList, User
from todo_list.utils import decode_token

security = Depends(HTTPBearer())
credentials_exception = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    'Invalid or expired token',
    {'Authenticate': 'Bearer'},
)


async def has_access(
        credentials: HTTPAuthorizationCredentials = security,
        db_session: AIOSession = Depends(get_db_session),
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
    if not user.is_superuser:
        task_id = str(user.celery_task_id.as_uuid())
        if task_id:
            AsyncResult(task_id).revoke()
        task_result = delete_user_after_inactive_period.apply_async(
            (username,),
            eta=datetime.datetime.utcnow() + datetime.timedelta(
                days=INACTIVE_DAYS,
            )
        )
        user.celery_task_id = Binary.from_uuid(UUID(task_result.id))
        await db_session.save(user)
    return user


async def get_todo_list_by_uuid(
        uuid: UUID,
        user: User = Depends(has_access),
        db_session: AIOSession = Depends(get_db_session),
) -> tuple[User, TODOList, AIOSession]:
    if user.is_superuser:
        todo_list = await db_session.find_one(
            TODOList,
            TODOList.uuid == Binary.from_uuid(uuid),
        )
    else:
        todo_list = await db_session.find_one(
            TODOList,
            TODOList.user == user.id,
            TODOList.uuid == Binary.from_uuid(uuid),
        )
    if not todo_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user, todo_list, db_session
