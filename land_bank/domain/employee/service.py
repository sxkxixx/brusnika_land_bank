from typing import Optional, Union
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.auth.hasher import Hasher
from infrastructure.database.model import Employee, Position, PermissionPosition
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository
from infrastructure.exception import rpc_exceptions

__all__ = [
	'EmployeeService'
]


class EmployeeService:
	def __init__(self):
		self.session: Union[AsyncSession, None] = None
		self.__employee_repository: Union[SQLAlchemyRepository, None] = None

	def set_async_session(self, session: AsyncSession) -> None:
		self.session: AsyncSession = session
		self.__employee_repository: SQLAlchemyRepository = (
			SQLAlchemyRepository(Employee))

	async def create_employee(
			self, **data) -> Employee:
		"""
		Создает и возвращает нового пользователя
		:param data:
		:return:
		"""
		try:
			employee: Employee = await (
				self.__employee_repository.create_record(
					email=data.get('email'),
					hashed_password=Hasher.get_password_hash(
						data.get('password')),
					last_name=data.get('last_name'),
					first_name=data.get('first_name'),
					patronymic=data.get('patronymic'),
					phone_number=data.get('phone_number'),
				))
			await self.session.commit()
		except IntegrityError:
			await self.session.rollback()
			raise rpc_exceptions.UniqueEmailError()
		finally:
			await self.session.close()
		return employee

	async def get_login_employee(
			self,
			password: str,
			*filters
	) -> Employee:
		employee: Employee = await self.__employee_repository.get_record(
			*filters)
		if employee is None:
			raise rpc_exceptions.LoginError(data='User is missed')
		if not Hasher.verify_password(password, employee.hashed_password):
			raise rpc_exceptions.LoginError(data='Incorrect password')
		return employee

	async def get_employee(self, *filters) -> Optional[Employee]:
		employee: Employee = await self.__employee_repository.get_record(
			*filters)
		if employee is None:
			return None
		return employee

	async def get_employee_with_permissions(self, *filters) -> Optional[
		Employee]:
		employee: Employee = await (
			self.__employee_repository.get_record_with_relationships(
				filters=filters,
				options=[selectinload(Employee.position).selectinload(
					Position.permissions).selectinload(
					PermissionPosition.permission)]
			))
		if employee is None:
			return None
		return employee

	async def set_employee_photo(
			self,
			employee: Employee,
			filename: str
	) -> Employee:
		try:
			employee: Employee = await self.__employee_repository.update_record(
				Employee.id == employee.id, Employee.email == employee.email,
				s3_avatar_file=filename
			)
			await self.session.commit()
			return employee
		except Exception as e:
			await self.session.commit()
			# TODO написать нормальную ошибку
			raise Exception(str(e))
		finally:
			await self.session.close()

	async def get_full_profile(self, employee_id: UUID) -> Employee:
		return await self.__employee_repository.get_record_with_relationships(
			filters=[
				Employee.id == employee_id
			],
			options=[
				selectinload(Employee.employee_head),
				selectinload(Employee.position),
				selectinload(Employee.department)
			]
		)

	async def update_profile_info(self, employee_id, **values_set) -> Employee:
		try:
			employee = await self.__employee_repository.update_record(
				Employee.id == employee_id,
				**values_set
			)
			await self.session.commit()
			return employee
		except Exception as e:
			await self.session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()
