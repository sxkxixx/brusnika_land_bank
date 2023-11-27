from typing import Type, Iterable

from sqlalchemy import select, update
from core import async_session
from .base import BaseRepository


class SQLAlchemyRepository(BaseRepository):
    _model = None

    async def create_record(self, **kwargs) -> _model:
        async with async_session() as session:
            record = self._model(**kwargs)
            session.add(record)
            await session.commit()
        return record

    async def get_record(self, *filters) -> _model:
        async with async_session() as session:
            statement = select(self._model).where(*filters)
            result = await session.scalar(statement)
        return result

    async def select_records(self, *args, **kwargs) -> Iterable[_model]:
        pass

    async def update_record(self, *filters, **values_set) -> _model:
        async with async_session() as session:
            statement = (
                update(self._model)
                .where(*filters)
                .values(**values_set)
                .returning(self._model)
            )
            result = await session.scalar(statement)
            await session.commit()
            return result

    async def get_record_with_relationships(self, *, filters,
                                            options) -> _model:
        async with async_session() as session:
            statement = select(self._model).where(*filters).options(*options)
            return await session.scalar(statement)
