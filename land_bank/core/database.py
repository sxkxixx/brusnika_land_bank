from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from .config import Config
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from sqlalchemy import MetaData

DATABASE_URL = (f'postgresql+asyncpg://'
                f'{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}'
                f'@{Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}'
                f'/{Config.POSTGRES_DB}')

async_engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

metadata = MetaData()


class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
