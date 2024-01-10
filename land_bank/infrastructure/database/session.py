from contextvars import ContextVar
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

from infrastructure.settings import DatabaseSettings

DATABASE_URL = (
    f'postgresql+asyncpg://'
    f'{DatabaseSettings.POSTGRES_USER}'
    f':{DatabaseSettings.POSTGRES_PASSWORD}'
    f'@{DatabaseSettings.POSTGRES_HOST}'
    f':{DatabaseSettings.POSTGRES_PORT}'
    f'/{DatabaseSettings.POSTGRES_DB}'
)

async_engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def async_session_generator() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


def get_async_session() -> AsyncSession:
    """
    :return: Сессия
    """
    return async_session()


ASYNC_CONTEXT_SESSION: ContextVar[AsyncSession] = ContextVar(
    'async_context_session',
)
