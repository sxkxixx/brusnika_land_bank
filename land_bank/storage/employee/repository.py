from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.auth.hasher import Hasher
from infrastructure.database.model import Employee, PermissionPosition, Position
from infrastructure.exception import rpc_exceptions
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository

__all__ = [
    'EmployeeRepository'
]


class EmployeeRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Employee)

    async def create_user(self, session: AsyncSession, **values_set):
        values_set.pop('password_repeat')
        pwd: str = values_set.pop('password')
        values_set['hashed_password'] = Hasher.get_password_hash(pwd)
        return await self.create_record(session, **values_set)

    async def get_employee(self, session: AsyncSession, *filters) -> Employee:
        employee: Employee = await self.get_record(session, *filters)
        if not employee:
            raise rpc_exceptions.ObjectNotFoundError()
        return employee

    async def get_employee_with_permissions(
            self,
            session: AsyncSession,
            *filters
    ) -> Optional[Employee]:
        """
        Возвращает пользоватея с его разрешениями
        :param session:
        :param filters:
        :return:
        """
        return await (
            self.get_record_with_relationships(
                session, filters=filters, options=[
                    selectinload(Employee.position)
                    .selectinload(Position.permissions)
                    .selectinload(PermissionPosition.permission)
                ]
            ))

    async def update_employee(self, session: AsyncSession, *filters,
                              **values_set) -> Employee:
        """
        Метод обновлять запись Employee в БД и возвращает обновленную запись
        :param session:
        :param filters: Параметры фильтрации
        :param values_set: Параметры для установки
        :return: Обновленную запись пользователя
        """
        employee: Employee = await self.update_record(
            session, *filters, **values_set)
        return employee

    async def employee_profile(
            self, session: AsyncSession, employee_id: UUID) -> Optional[
        Employee]:
        """
        Возвращает запись пользователя с отношениями employee_head, position,
        department
        :param session:
        :param employee_id: ID сотрудника
        :return:
        """
        employee: Employee = await self.get_record_with_relationships(
            session, filters=[Employee.id == employee_id],
            options=[
                selectinload(Employee.employee_head),
                selectinload(Employee.position),
                selectinload(Employee.department)
            ]
        )
        return employee
