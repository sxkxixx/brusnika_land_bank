from typing import Type, Iterable

from sqlalchemy import select
from core import async_session
from .base import BaseRepository


class SQLAlchemyRepository(BaseRepository):
    _model = None
    model_type = Type['_model']

    async def create_record(self, **kwargs) -> model_type:
        async with async_session() as session:
            record = self._model(**kwargs)
            session.add(record)
            await session.commit()
        return record

    async def get_record(self, *filters) -> model_type:
        async with async_session() as session:
            statement = select(self._model).where(*filters)
            result = await session.scalar(statement)
        return result

    async def select_records(self, *args, **kwargs) -> Iterable[model_type]:
        pass

    async def update_record(self, *args, **kwargs) -> model_type:
        pass
