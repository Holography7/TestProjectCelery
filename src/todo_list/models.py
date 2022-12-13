import datetime
from typing import Generator
from uuid import uuid4

from bson import Binary
from odmantic import Field, Index, Model, Reference


class User(Model):
    username: str = Field(unique=True)
    password: str
    telegram: str
    last_seen: datetime.datetime
    is_superuser: bool = False


class TODOList(Model):
    uuid: Binary = Field(
        default_factory=lambda: Binary.from_uuid(uuid4()),
        unique=True,
    )
    name: str
    user: User = Reference()

    class Config:
        @staticmethod
        def indexes() -> Generator[Index, None, None]:
            yield Index(TODOList.name, TODOList.user, unique=True)


class Task(Model):
    uuid: Binary = Field(
        default_factory=lambda: Binary.from_uuid(uuid4()),
        unique=True,
    )
    name: str
    is_complete: bool
    todo_list: TODOList = Reference()

    class Config:
        @staticmethod
        def indexes() -> Generator[Index, None, None]:
            yield Index(Task.name, Task.todo_list, unique=True)
