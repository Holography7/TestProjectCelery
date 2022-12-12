from fastapi import FastAPI
from httpx import AsyncClient

from todo_list.models import User
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


async def test_admin_profile(app: FastAPI, access_token: str) -> None:
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token}'},
    ) as async_client:
        response = await async_client.get('/profile')
    assert response.status_code == 200, response.json()
    assert response.json() == {'username': 'admin', 'telegram': '@admin'}


async def test_registration(
        app: FastAPI,
        user_registration_data: dict,
) -> None:
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post(
            '/registration',
            json=user_registration_data,
        )
    assert response.status_code == 201, response.json()


async def test_get_tokens(app: FastAPI, admin: User) -> None:
    auth_data = {'username': admin.username, 'password': ADMIN_PASSWORD}
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post('/tokens', json=auth_data)
    assert response.status_code == 201, response.json()


async def test_refresh_tokens(app: FastAPI, refresh_token: str) -> None:
    data = {'refresh_token': refresh_token}
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post('/tokens/refresh', json=data)
    assert response.status_code == 201, response.json()
