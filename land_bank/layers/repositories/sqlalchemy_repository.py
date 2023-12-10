from functools import wraps
from typing import Iterable
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core import async_session
from .base import BaseRepository


# Unusable
async def in_transaction(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session = async_session()
        try:
            result = await func(session, *args, **kwargs)
            await session.commit()
        finally:
            await session.rollback()
            await session.close()
        return result

    return wrapper


class SQLAlchemyRepositoryV1(BaseRepository):
    _model = None

    def __init__(self, session: AsyncSession):
        """
        :param session: Активная сессия
        """
        self.session = session

    async def create_record(self, **kwargs) -> _model:
        """
        Создает запись в базе данных и возвращает её
        :param kwargs: Значения
        :return: Новую запись в БД
        """
        statement = insert(self._model).values(**kwargs).returning(self._model)
        result = await self.session.scalar(statement)
        return result

    async def get_record(self, *filters) -> _model:
        """
        Возвращает запись по фильтрам
        :param filters: Параметры фильтрации
        :return: Запись
        """
        statement = select(self._model).where(*filters)
        result = await self.session.scalar(statement)
        return result

    async def select_records(
            self,
            filters,
            options,
            orders,
            **kwargs
    ) -> Iterable[_model]:
        """
        Выбирает записи с параметрами фильтрации, отношениями и сортировками
        :param filters: Параметры фильтрации
        :param options: Параметры для выбора отношений
        :param orders: Параметры для сортировки
        :param kwargs: {"limit": int, "offset": int}
        :return: Список записей
        """
        limit, offset = kwargs.get('limit'), kwargs.get('offset')
        statement = (
            select(self._model)
            .where(*filters)
            .options(*options)
            .order_by(*orders)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def update_record(self, *filters, **values_set) -> _model:
        """
        Обновляет запись и возвращает её
        :param filters: Параметры фильтрации
        :param values_set: Параметры для установки
        :return: Возвращает обновлённую запись
        """
        statement = (
            update(self._model)
            .where(*filters)
            .values(**values_set)
            .returning(self._model)
        )
        result = await self.session.execute(statement)
        return result.scalar()

    async def get_record_with_relationships(
            self,
            *,
            filters,
            options
    ) -> _model:
        statement = select(self._model).where(*filters).options(*options)
        return await self.session.scalar(statement)

    async def get_or_create_record(self, **kwargs) -> _model:
        record = await self.session.scalar(select(self._model).filter_by(**kwargs))
        if not record:
            record = self._model(**kwargs)
            self.session.add(record)
        return record
