import datetime

from odmantic import Field, Model


class User(Model):
    username: str = Field(unique=True)
    password: str
    telegram: str
    last_seen: datetime.datetime
    is_superuser: bool = False


class Task(Model):
    name: str
    is_complete: bool


class TODOList(Model):
    name: str
    tasks: list[Task]
