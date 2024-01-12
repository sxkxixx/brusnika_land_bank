from typing import Dict, Any, Union
from typing import Optional

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi_jsonrpc import API
from httpx import AsyncClient

from domain.employee import EmployeeCreateSchema, EmployeeLoginSchema
from main import app

TEST_USER_SCHEMA = EmployeeCreateSchema(
    email='test@mail.ru', password='password', password_repeat='password'
)
LOGIN_SCHEMA = EmployeeLoginSchema(
    email='test@mail.ru', password='password'
)

AUTH_APP_URL = 'http://localhost:8000/api/v1/auth'
REGISTER_USER_METHOD: str = "register_user"
LOGIN_USER_METHOD: str = "login_user"


class RequestSender:
    _Body = Dict[str, Any]

    def __init__(self, _app: Union[FastAPI, API] = app):
        self.app = _app

    async def __call__(self, url: str, json_body: _Body) -> _Body:
        """
        Отправляет Post запрос
        :param url: URL адрес эндпоинта
        :param json_body: Тело запроса
        :return: Ответ от сервера
        """
        async with LifespanManager(app=self.app):
            async with AsyncClient(app=self.app) as async_client:
                response = await async_client.post(url=url, json=json_body)
        return response.json()


@pytest.fixture(scope='module')
def request_sender() -> RequestSender:
    return RequestSender(app)


class RPCRequest:
    def get_request_body(
            self,
            method: str,
            json_body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Возвращае json (словарь) с телом запроса для json-rpc метода
        :param method: Метод
        :param json_body: Параметры для params
        :return: Тело запроса
        """
        return {
            "jsonrpc": "2.0",
            "id": "0",
            "method": method,
            "params": json_body if json_body else {}
        }


@pytest.fixture(scope='module')
def rpc_request() -> RPCRequest:
    return RPCRequest()


@pytest.fixture(scope='function')
async def jwt_token(
        rpc_request: RPCRequest,
        request_sender: RequestSender
) -> str:
    await request_sender(
        AUTH_APP_URL,
        json_body=rpc_request.get_request_body(
            REGISTER_USER_METHOD, TEST_USER_SCHEMA.model_dump()
        )
    )
    response = await request_sender(
        AUTH_APP_URL,
        json_body=rpc_request.get_request_body(LOGIN_USER_METHOD)
    )
    return response.get('result', {}).get('access_token')
