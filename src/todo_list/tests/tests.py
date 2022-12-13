from fastapi import FastAPI
from httpx import AsyncClient
from odmantic import AIOEngine

from todo_list.models import TODOList, User
from todo_list.tests.factories import ADMIN_PASSWORD


async def test_health_check(app: FastAPI) -> None:
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.get('/health')
    assert response.status_code == 200, response.json()
    assert response.json() == {'Database': 'OK'}


async def test_profile(app: FastAPI) -> None:
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.get('/profile')
    assert response.status_code == 403, response.json()


async def test_admin_profile(app: FastAPI, access_token_admin: str) -> None:
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token_admin}'},
    ) as async_client:
        response = await async_client.get('/profile')
    assert response.status_code == 200, response.json()
    assert response.json() == {'username': 'admin', 'telegram': '@admin'}


async def test_registration(
        app: FastAPI,
        user_registration_data: dict,
        mongo_test_engine: AIOEngine,
) -> None:
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post(
            '/registration',
            json=user_registration_data,
        )
    assert response.status_code == 201, response.json()
    async with mongo_test_engine.session() as session:
        assert await session.find_one(
            User,
            User.username == response.json()['username'],
        )


async def test_get_tokens(app: FastAPI, admin: User) -> None:
    auth_data = {'username': admin.username, 'password': ADMIN_PASSWORD}
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post('/tokens', json=auth_data)
    assert response.status_code == 201, response.json()


async def test_refresh_tokens(app: FastAPI, refresh_token_admin: str) -> None:
    data = {'refresh_token': refresh_token_admin}
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post('/tokens/refresh', json=data)
    assert response.status_code == 201, response.json()


async def test_create_todo_list(
        app: FastAPI,
        access_token: str,
        todo_list_create_data: dict,
        mongo_test_engine: AIOEngine,
) -> None:
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token}'},
    ) as async_client:
        response = await async_client.post(
            '/todo_list/create',
            json=todo_list_create_data,
        )
    response_json = response.json()
    assert response.status_code == 201, response_json
    response_json.pop('uuid')
    assert response_json == todo_list_create_data
    async with mongo_test_engine.session() as session:
        assert await session.find_one(
            TODOList,
            TODOList.name == response_json['name'],
        )


async def test_get_todo_list_as_common_user(
        app: FastAPI,
        common_user: User,
        access_token: str,
        todo_lists: list[TODOList],
        mongo_test_engine: AIOEngine,
) -> None:
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token}'},
    ) as async_client:
        response = await async_client.get('/todo_list')
    response_json = response.json()
    assert response.status_code == 200, response_json
    async with mongo_test_engine.session() as session:
        user_todo_lists = await session.find(
            TODOList,
            TODOList.user == common_user.id,
        )
    true_response = [todo_list.dict() for todo_list in user_todo_lists]
    for todo_list in true_response:
        todo_list.pop('id')
        todo_list.pop('user')
        todo_list['uuid'] = str(todo_list['uuid'].as_uuid())
    assert true_response == response_json


async def test_get_todo_list_as_admin(
        app: FastAPI,
        access_token_admin: str,
        todo_lists: list[TODOList],
) -> None:
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token_admin}'},
    ) as async_client:
        response = await async_client.get('/todo_list')
    response_json = response.json()
    assert response.status_code == 200, response_json
    true_response = [todo_list.dict() for todo_list in todo_lists]
    for todo_list in true_response:
        todo_list.pop('id')
        todo_list.pop('user')
        todo_list['uuid'] = str(todo_list['uuid'].as_uuid())
    assert true_response == response_json
