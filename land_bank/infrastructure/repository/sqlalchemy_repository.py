from typing import Iterable, List, Optional, Type

from sqlalchemy import Executable, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.model import DatabaseEntity
from .interface import Repository


class SQLAlchemyRepository(Repository):
    def __init__(
            self,
            model: Type[DatabaseEntity]
    ):
        """:param model: Модель"""
        self.__model: Type[DatabaseEntity] = model

    async def create_record(
            self,
            session: AsyncSession,
            **kwargs
    ) -> DatabaseEntity:
        """
        Создает запись в базе данных и возвращает её
        :param session: Сессия БД
        :param kwargs: Значения
        :return: Новую запись в БД
        """
        statement: Executable = insert(self.__model).values(
            **kwargs).returning(
            self.__model)
        result = await session.scalar(statement)
        return result

    async def get_record(
            self,
            session: AsyncSession,
            *filters
    ) -> DatabaseEntity:
        """
        Возвращает запись по фильтрам
        :param session: Сессия БД
        :param filters: Параметры фильтрации
        :return: Запись
        """
        statement: Executable = select(self.__model).where(*filters)
        result = await session.scalar(statement)
        return result

    async def full_select_records(
            self,
            session: AsyncSession,
            filters,
            options,
            orders,
            **kwargs
    ) -> Iterable[DatabaseEntity]:
        """
        Выбирает записи с параметрами фильтрации, отношениями и сортировками
        :param session: Сессия БД
        :param filters: Параметры фильтрации
        :param options: Параметры для выбора отношений
        :param orders: Параметры для сортировки
        :param kwargs: {"limit": int, "offset": int}
        :return: Список записей
        """
        limit, offset = kwargs.get('limit'), kwargs.get('offset')
        statement: Executable = (
            select(self.__model)
            .where(*filters)
            .options(*options)
            .order_by(*orders)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(statement)
        return result.scalars().all()

    async def select_records(
            self,
            session: AsyncSession,
            filters,
            options
    ) -> Iterable[DatabaseEntity]:
        statement: Executable = (
            select(self.__model)
            .where(*filters)
            .options(*options)
        )
        result = await session.scalars(statement)
        return result

    async def select_ordered_records(
            self,
            session: AsyncSession,
            offset: int,
            limit: int,
            options: Optional[List] = None,
            orders: Optional[List] = None,
    ) -> Iterable[DatabaseEntity]:
        statement: Executable = (
            select(self.__model)  # type: ignore
            .options(*options)
            .order_by(*orders)
            .offset(offset)
            .limit(limit)
        )
        result = await session.scalars(statement)
        return result.all()

    async def update_record(
            self,
            session: AsyncSession,
            *filters,
            **values_set
    ) -> DatabaseEntity | None:
        """
        Обновляет запись и возвращает её
        :param session: Сессия БД
        :param filters: Параметры фильтрации
        :param values_set: Параметры для установки
        :return: Возвращает обновлённую запись
        """
        statement: Executable = (
            update(self.__model)
            .where(*filters)
            .values(**values_set)
            .returning(self.__model)
        )
        result = await session.execute(statement)
        return result.scalar()

    async def get_record_with_relationships(
            self,
            session: AsyncSession,
            filters,
            options
    ) -> Optional[DatabaseEntity]:
        """
        :param session: Сессия БД
        :param filters: Параметры фильтрации
        :param options: Параметры подгрузки отношений
        :return:
        """
        statement: Executable = select(self.__model).where(*filters).options(
            *options)
        return await session.scalar(statement)

    async def delete_record(
            self,
            session: AsyncSession,
            instance: 'DatabaseEntity'
    ) -> None:
        await self.delete_record(session, instance)
