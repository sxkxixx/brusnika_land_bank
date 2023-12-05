from main import app
import pytest
from httpx import AsyncClient
from asgi_lifespan import LifespanManager

from tests.utils import json_rpc_body

DEFAULT_USER = {
    "email": "zembank@gmail.com",
    "password": "f79cdd441981",
    "password_repeat": "f79cdd441981",
    "last_name": "Иванов",
    "first_name": "Иван",
    "patronymic": "Иванович",
    "phone_number": "+79920205250"
}


@pytest.mark.asyncio
async def test_assert_correct_register_method():
    """Проверяет, что пользователь буден создан, при корректно переданных параметрах"""
    user = DEFAULT_USER.copy()
    body: dict = json_rpc_body(
        method='register_user',
        params={'user': user}
    )
    async with LifespanManager(app):
        async with AsyncClient(
                app=app,
                base_url='http://127.0.0.1:8000/api/v1'
        ) as async_client:
            response = await async_client.post(url='/auth', json=body)
    json = response.json()
    assert response.status_code == 200, 'Статус не равен 200'
    assert json['result']['email'] == 'zembank@gmail.com'


@pytest.mark.asyncio
async def test_assert_different_passwords():
    """Проверяет, что пользователь не будет создан, так как пароли не совпадают"""
    user = DEFAULT_USER.copy()
    user['password'] = 'passwordpassword1'
    user['password_repeat'] = 'passwordpassword2'
    body: dict = json_rpc_body(
        method='register_user',
        params={'user': user}
    )
    async with LifespanManager(app):
        async with AsyncClient(
                app=app,
                base_url='http://127.0.0.1:8000/api/v1'
        ) as async_client:
            response = await async_client.post(url='/auth', json=body)
    json = response.json()

    assert json['error']['code'] == -32602, 'ValidationError не выбрасилось'
    assert json['error']['message'] == 'Invalid params'


@pytest.mark.asyncio
async def test_assert_incorrect_password_length():
    """Проверяет, что пользователь не будет создан, так как пароль неверной длины"""
    user = DEFAULT_USER.copy()
    user['password'] = user['password_repeat'] = 'lte12symb'
    body: dict = json_rpc_body(
        method='register_user',
        params={'user': user}
    )
    async with LifespanManager(app):
        async with AsyncClient(
                app=app,
                base_url='http://127.0.0.1:8000/api/v1'
        ) as async_client:
            response = await async_client.post(url='/auth', json=body)
    json = response.json()

    assert json['error']['code'] == -32602, 'ValidationError не выбрасилось'
    assert json['error']['message'] == 'Invalid params'


@pytest.mark.asyncio
async def test_assert_incorrect_email():
    """Проверяет, что пользователь не будет создан, так как неправильный email"""
    user = DEFAULT_USER.copy()
    user['email'] = 'zembank'
    body: dict = json_rpc_body(
        method='register_user',
        params={'user': user}
    )
    async with LifespanManager(app):
        async with AsyncClient(
                app=app,
                base_url='http://127.0.0.1:8000/api/v1'
        ) as async_client:
            response = await async_client.post(url='/auth', json=body)
    json = response.json()

    assert json['error']['code'] == -32602, 'ValidationError не выбрасилось'
    assert json['error']['message'] == 'Invalid params'


