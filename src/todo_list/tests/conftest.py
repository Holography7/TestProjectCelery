import asyncio
import random
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator

from database import mongo_client
from dependencies import get_db_session
from fastapi import FastAPI
from main import app as fastapi_app
from odmantic import AIOEngine
from odmantic.session import AIOSession
from pytest import fixture

from todo_list.enums import TokenEnum
from todo_list.models import TODOList, User
from todo_list.tests.factories import (
    TODOListCreateFactory,
    TODOListFactory,
    UserAdminFactory,
    UserFactory,
    UserRegistrationFactory,
)
from todo_list.utils import create_token

TEST_DATABASE = 'pytest'


@fixture(scope='session')
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@fixture(scope='session')
async def mongo_test_engine() -> AsyncGenerator[AIOEngine, None]:
    engine = AIOEngine(client=mongo_client, database=TEST_DATABASE)
    yield engine
    await mongo_client.drop_database(TEST_DATABASE)


@fixture(scope='session')
def app(mongo_test_engine: AIOEngine) -> FastAPI:
    async def override_get_db_session() -> AsyncGenerator[AIOSession, None]:
        async with mongo_test_engine.session() as session:
            yield session

    fastapi_app.dependency_overrides[get_db_session] = override_get_db_session
    return fastapi_app


@fixture(scope='session')
async def admin(mongo_test_engine: AIOEngine) -> User:
    user = UserAdminFactory()
    async with mongo_test_engine.session() as session:
        await session.save(user)
    return user


@fixture(scope='session')
def access_token_admin(admin: User) -> str:
    return create_token(admin.username)


@fixture(scope='session')
def refresh_token_admin(admin: User) -> str:
    return create_token(admin.username, token_type=TokenEnum.REFRESH)


@fixture(scope='session')
async def common_user(mongo_test_engine: AIOEngine) -> User:
    user = UserFactory()
    async with mongo_test_engine.session() as session:
        await session.save(user)
    return user


@fixture
def user_registration_data() -> dict:
    return UserRegistrationFactory().dict()


@fixture
def access_token(common_user: User) -> str:
    return create_token(common_user.username)


@fixture
def refresh_token(common_user: User) -> str:
    return create_token(common_user.username, token_type=TokenEnum.REFRESH)


@fixture
def todo_list_create_data() -> dict:
    return TODOListCreateFactory().dict()


@fixture
async def todo_lists(
        admin: User,
        common_user: User,
        mongo_test_engine: AIOEngine,
) -> AsyncGenerator[list[TODOListFactory], None]:
    todo_lists = [
        TODOListFactory(user=random.choice((admin, common_user)))
        for i in range(5)
    ]
    async with mongo_test_engine.session() as session:
        await session.save_all(todo_lists)
    yield todo_lists
    await mongo_test_engine.remove(TODOList)
