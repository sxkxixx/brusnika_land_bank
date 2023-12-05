from main import app
import pytest
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from auth.token_service import TokenService
from auth.refresh_session import RefreshSession
import pytest_asyncio
from tests.utils import json_rpc_body

DEFAULT_USER_CREATE = {
    "email": "zembank@gmail.com",
    "password": "f79cdd441981",
    "password_repeat": "f79cdd441981",
    "last_name": "Иванов",
    "first_name": "Иван",
    "patronymic": "Иванович",
    "phone_number": "+79920205250"
}

DEFAULT_USER_LOGIN = {
    "email": "zembank@gmail.com",
    "password": "f79cdd441981",
}


@pytest_asyncio.fixture
async def register_user():
    user = DEFAULT_USER_CREATE.copy()
    body: dict = json_rpc_body(
        method='register_user',
        params={'user': user}
    )
    async with LifespanManager(app):
        async with AsyncClient(
                app=app,
                base_url='http://127.0.0.1:8000/api/v1'
        ) as async_client:
            await async_client.post(url='/auth', json=body)


@pytest.mark.asyncio
async def test_login_user_exists(register_user):
    user = DEFAULT_USER_LOGIN.copy()
    body = json_rpc_body(
        method='login_user',
        params={'login_data': user}
    )
    async with LifespanManager(app=app):
        async with AsyncClient(
                app=app,
                base_url='http://127.0.0.1:8000/api/v1'
        ) as async_client:
            response = await async_client.post(url='/auth', json=body)

    json = response.json()
    print(json)
    payload = TokenService.get_token_payload(json['result']['access_token'])
    refresh_session = await RefreshSession.get_by_key(
        response.cookies.get('refresh_token'))
    assert payload.get('email') == user.get('email')
    assert refresh_session is not None
