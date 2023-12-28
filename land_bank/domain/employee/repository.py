from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.hasher import Hasher
from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from infrastructure.exception import rpc_exceptions
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository
from infrastructure.database.model import Employee

__all__ = [
	'EmployeeRepository'
]


class EmployeeRepository(SQLAlchemyRepository):
	def __init__(self):
		session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
		super().__init__(session, Employee)

	async def create_user(self, **values_set):
		return await self.create_record(
			email=values_set.get('email'),
			hashed_password=Hasher.get_password_hash(
				values_set.get('password')),
			last_name=values_set.get('last_name'),
			first_name=values_set.get('first_name'),
			patronymic=values_set.get('patronymic'),
			phone_number=values_set.get('phone_number'),
		)

	async def get_employee(self, *filters) -> Employee:
		employee: Employee = await self.get_record(*filters)
		if not employee:
			raise rpc_exceptions.ObjectDoesNotExistsError()
		return employee
