from typing import Type, Iterable
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository


class SQLAlchemyRepository(BaseRepository):
    _model = None
    model_type = Type['_model']

    def __init__(self, async_session: AsyncSession):
        self.session: AsyncSession = async_session

    async def create_record(self, **kwargs) -> model_type:
        record = self._model(**kwargs)
        self.session.add(record)
        return record

    async def get_record(self, *args, **kwargs) -> model_type:
        pass

    async def select_records(self, *args, **kwargs) -> Iterable[model_type]:
        pass

    async def update_record(self, *args, **kwargs) -> model_type:
        pass

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
        await self.session.close()
