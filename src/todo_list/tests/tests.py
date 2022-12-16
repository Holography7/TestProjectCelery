from uuid import UUID

from bson import Binary
from fastapi import FastAPI
from httpx import AsyncClient
from odmantic import AIOEngine
from pytest_mock import MockerFixture

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
            '/todo_list',
            json=todo_list_create_data,
        )
    response_json = response.json()
    assert response.status_code == 201, response_json
    uuid = UUID(response_json.pop('uuid'))
    assert response_json == todo_list_create_data
    async with mongo_test_engine.session() as session:
        assert await session.find_one(
            TODOList,
            TODOList.uuid == Binary.from_uuid(uuid),
        )


async def test_get_todo_lists_as_common_user(
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


async def test_get_todo_lists_as_admin(
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


async def test_get_todo_list_as_common_user(
        app: FastAPI,
        common_user: User,
        access_token: str,
        todo_lists: list[TODOList],
) -> None:
    todo_list = None
    for lst in todo_lists:
        if lst.user.id == common_user.id:
            todo_list = lst
            break
    assert todo_list is not None, \
        'TODOList not created for current user (bad fixture?)'
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token}'},
    ) as async_client:
        response = await async_client.get(
            f'/todo_list/{todo_list.uuid.as_uuid()}',
        )
    response_json = response.json()
    assert response.status_code == 200, response_json
    true_response = todo_list.dict()
    true_response.pop('id')
    true_response.pop('user')
    true_response['uuid'] = str(true_response['uuid'].as_uuid())
    assert true_response == response_json


async def test_get_todo_list_as_admin(
        app: FastAPI,
        access_token_admin: str,
        todo_lists: list[TODOList],
) -> None:
    todo_list = todo_lists[0]
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token_admin}'},
    ) as async_client:
        response = await async_client.get(
            f'/todo_list/{todo_list.uuid.as_uuid()}',
        )
    response_json = response.json()
    assert response.status_code == 200, response_json
    true_response = todo_list.dict()
    true_response.pop('id')
    true_response.pop('user')
    true_response['uuid'] = str(true_response['uuid'].as_uuid())
    assert true_response == response_json


async def test_get_admin_todo_list_as_common_user(
        app: FastAPI,
        common_user: User,
        access_token: str,
        todo_lists: list[TODOList],
) -> None:
    todo_list = None
    for lst in todo_lists:
        if lst.user.id != common_user.id:
            todo_list = lst
            break
    assert todo_list is not None, \
        'TODOList not created for admin (bad fixture?)'
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token}'},
    ) as async_client:
        response = await async_client.get(
            f'/todo_list/{todo_list.uuid.as_uuid()}',
        )
    response_json = response.json()
    assert response.status_code == 404, response_json


async def test_put_todo_list_as_common_user(
        app: FastAPI,
        common_user: User,
        access_token: str,
        todo_lists: list[TODOList],
        todo_list_create_data: dict,
        mongo_test_engine: AIOEngine,
) -> None:
    todo_list = None
    for lst in todo_lists:
        if lst.user.id == common_user.id:
            todo_list = lst
            break
    assert todo_list is not None, \
        'TODOList not created for common user (bad fixture?)'
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token}'},
    ) as async_client:
        response = await async_client.put(
            f'/todo_list/{todo_list.uuid.as_uuid()}',
            json=todo_list_create_data,
        )
    response_json = response.json()
    assert response.status_code == 200, response_json
    async with mongo_test_engine.session() as session:
        todo_list_db = await session.find_one(
            TODOList,
            TODOList.uuid == Binary.from_uuid(UUID(response_json['uuid'])),
        )
    assert todo_list_db is not None, 'TODOList not found in DB (bad uuid?)'
    true_response = todo_list_db.dict()
    true_response.pop('id')
    true_response.pop('user')
    true_response['uuid'] = str(true_response['uuid'].as_uuid())
    assert true_response == response_json


async def test_put_todo_list_as_admin(
        app: FastAPI,
        access_token_admin: str,
        todo_lists: list[TODOList],
        todo_list_create_data: dict,
        mongo_test_engine: AIOEngine,
) -> None:
    todo_list = todo_lists[0]
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token_admin}'},
    ) as async_client:
        response = await async_client.put(
            f'/todo_list/{todo_list.uuid.as_uuid()}',
            json=todo_list_create_data,
        )
    response_json = response.json()
    assert response.status_code == 200, response_json
    async with mongo_test_engine.session() as session:
        todo_list_db = await session.find_one(
            TODOList,
            TODOList.uuid == Binary.from_uuid(UUID(response_json['uuid'])),
        )
    assert todo_list_db is not None, 'TODOList not found in DB (bad uuid?)'
    true_response = todo_list_db.dict()
    true_response.pop('id')
    true_response.pop('user')
    true_response['uuid'] = str(true_response['uuid'].as_uuid())
    assert true_response == response_json


async def test_put_admin_todo_list_as_common_user(
        app: FastAPI,
        common_user: User,
        access_token: str,
        todo_lists: list[TODOList],
        todo_list_create_data: dict,
        mongo_test_engine: AIOEngine,
) -> None:
    todo_list = None
    for lst in todo_lists:
        if lst.user.id != common_user.id:
            todo_list = lst
            break
    assert todo_list is not None, \
        'TODOList not created for common user (bad fixture?)'
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token}'},
    ) as async_client:
        response = await async_client.put(
            f'/todo_list/{todo_list.uuid.as_uuid()}',
            json=todo_list_create_data,
        )
    response_json = response.json()
    assert response.status_code == 404, response_json


async def test_delete_todo_list_as_common_user(
        app: FastAPI,
        common_user: User,
        access_token: str,
        todo_lists: list[TODOList],
        todo_list_create_data: dict,
        mongo_test_engine: AIOEngine,
) -> None:
    todo_list = None
    for lst in todo_lists:
        if lst.user.id == common_user.id:
            todo_list = lst
            break
    assert todo_list is not None, \
        'TODOList not created for common user (bad fixture?)'
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token}'},
    ) as async_client:
        response = await async_client.delete(
            f'/todo_list/{todo_list.uuid.as_uuid()}',
        )
    assert response.status_code == 204
    async with mongo_test_engine.session() as session:
        deleted_todo_list = await session.find_one(
            TODOList,
            TODOList.uuid == todo_list.uuid,
        )
    assert deleted_todo_list is None


async def test_delete_todo_list_as_admin(
        app: FastAPI,
        access_token_admin: str,
        todo_lists: list[TODOList],
        mongo_test_engine: AIOEngine,
        mocker: MockerFixture,
) -> None:
    mocked_celery_task = mocker.patch(
        'celery_app.tasks.send_message_about_deleting.delay',
    )
    mocked_celery_task.return_value = None
    todo_list = todo_lists[0]
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token_admin}'},
    ) as async_client:
        response = await async_client.delete(
            f'/todo_list/{todo_list.uuid.as_uuid()}',
        )
    assert response.status_code == 204
    async with mongo_test_engine.session() as session:
        deleted_todo_list = await session.find_one(
            TODOList,
            TODOList.uuid == todo_list.uuid,
        )
    assert deleted_todo_list is None


async def test_delete_admin_todo_list_as_common_user(
        app: FastAPI,
        common_user: User,
        access_token: str,
        todo_lists: list[TODOList],
        todo_list_create_data: dict,
        mongo_test_engine: AIOEngine,
) -> None:
    todo_list = None
    for lst in todo_lists:
        if lst.user.id != common_user.id:
            todo_list = lst
            break
    assert todo_list is not None, \
        'TODOList not created for common user (bad fixture?)'
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token}'},
    ) as async_client:
        response = await async_client.delete(
            f'/todo_list/{todo_list.uuid.as_uuid()}',
        )
    assert response.status_code == 404


async def test_delete_todo_list_of_common_user_as_admin(
        app: FastAPI,
        admin: User,
        access_token_admin: str,
        todo_lists: list[TODOList],
        mongo_test_engine: AIOEngine,
        mocker: MockerFixture,
) -> None:
    mocked_celery_task = mocker.patch(
        'celery_app.tasks.send_message_about_deleting.delay',
    )
    mocked_celery_task.return_value = None
    todo_list = None
    for lst in todo_lists:
        if lst.user.id != admin.id:
            todo_list = lst
            break
    assert todo_list is not None, \
        'TODOList not created for common user (bad fixture?)'
    async with AsyncClient(
            app=app,
            base_url='http://test',
            headers={'Authorization': f'Bearer {access_token_admin}'},
    ) as async_client:
        response = await async_client.delete(
            f'/todo_list/{todo_list.uuid.as_uuid()}',
        )
    assert response.status_code == 204
    async with mongo_test_engine.session() as session:
        deleted_todo_list = await session.find_one(
            TODOList,
            TODOList.uuid == todo_list.uuid,
        )
    assert deleted_todo_list is None
