# Fixture Scope
# session - На уровне всех тестов
# package - на уровне папки
# module - на уровне модуля
# class - ...
# function - на уровне функции
import logging
from typing import Union, AsyncGenerator, Dict, Any

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi_jsonrpc import API
from httpx import AsyncClient
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, \
    AsyncSession, async_sessionmaker

from infrastructure.database import Base
from infrastructure.settings import TestDatabaseSettings
from main import app

logging.basicConfig(level='INFO')

_TypeEngine = Union[Engine, AsyncEngine]

engine: _TypeEngine = create_async_engine(
    url=TestDatabaseSettings.url()
)
engine.echo = True

session_factory = async_sessionmaker(
    bind=engine,  # type: ignore
    class_=AsyncSession
)


@pytest.fixture(scope='function')
def session() -> AsyncSession:
    return session_factory()


@pytest.fixture(scope='function', autouse=True)
async def setup_database(session: AsyncSession) -> AsyncGenerator:
    """
    Lifespan для тестов
    :param session:
    :return:
    """
    try:
        await create_tables(engine, session)
        yield
        await drop_tables(engine, session)
    except Exception as e:
        print(e.args)


async def create_tables(_engine: _TypeEngine, session: AsyncSession) -> None:
    """
    Создает таблицы в БД
    :param _engine:
    :param session:
    :return:
    """
    Base.metadata.create_all(engine)  # type: ignore
    await session.commit()
    logging.info("Tables are created")


async def drop_tables(_engine: _TypeEngine, session: AsyncSession) -> None:
    """
    Удаляет все таблицы из БД
    :param _engine:
    :param session:
    :return:
    """
    await session.rollback()
    Base.metadata.drop_all(_engine)  # type: ignore
    await session.commit()
    logging.info("Tables are dropped")


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


@pytest.fixture(scope='session')
def request_sender() -> RequestSender:
    return RequestSender(app)
