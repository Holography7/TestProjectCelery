import asyncio
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator

from database import mongo_client
from fastapi import FastAPI
from main import app as fastapi_app
from odmantic import AIOEngine
from pytest import fixture

from todo_list.enums import TokenEnum
from todo_list.models import User
from todo_list.tests.factories import UserAdminFactory, UserRegistrationFactory
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
    return fastapi_app


@fixture(scope='session')
async def admin(mongo_test_engine: AIOEngine) -> User:
    user = UserAdminFactory()
    async with mongo_test_engine.session() as session:
        await session.save(user)
    return user


@fixture(scope='session')
def access_token(admin: User) -> str:
    return create_token(admin.username)


@fixture(scope='session')
def refresh_token(admin: User) -> str:
    return create_token(admin.username, token_type=TokenEnum.REFRESH)


@fixture()
def user_registration_data() -> dict:
    return UserRegistrationFactory().dict()
