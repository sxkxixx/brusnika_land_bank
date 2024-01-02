from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.auth.hasher import Hasher
from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from infrastructure.database.transaction import in_transaction
from infrastructure.exception import rpc_exceptions
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository
from infrastructure.database.model import Employee, PermissionPosition, Position

__all__ = [
	'EmployeeRepository'
]


class EmployeeRepository(SQLAlchemyRepository):
	def __init__(self):
		super().__init__(Employee)

	@in_transaction
	async def create_user(self, **values_set):
		values_set.pop('password_repeat')
		pwd: str = values_set.pop('password')
		values_set['hashed_password'] = Hasher.get_password_hash(pwd)
		session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
		return await self.create_record(session, **values_set)

	@in_transaction
	async def get_employee(self, *filters) -> Employee:
		session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
		employee: Employee = await self.get_record(session, *filters)
		if not employee:
			raise rpc_exceptions.ObjectDoesNotExistsError()
		return employee

	@in_transaction
	async def get_employee_with_permissions(self, *filters) -> Optional[
		Employee]:
		session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
		return await (
			self.get_record_with_relationships(
				session, filters=filters, options=[
					selectinload(Employee.position)
					.selectinload(Position.permissions)
					.selectinload(PermissionPosition.permission)
				]
			))
