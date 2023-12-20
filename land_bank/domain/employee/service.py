from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.auth.hasher import Hasher
from infrastructure.database.model import Employee, Position, PermissionPosition
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository

__all__ = [
	'EmployeeService'
]


class EmployeeService:
	def __init__(self, session: AsyncSession):
		self.session: AsyncSession = session
		self.__employee_repository = SQLAlchemyRepository(
			session, Employee)

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
			raise UniqueEmailError()
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
			raise LoginError(data='User is missed')
		if not Hasher.verify_password(password, employee.hashed_password):
			raise LoginError(data='Incorrect password')
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
		employee: Employee = await self.__employee_repository.update_record(
			Employee.id == employee.id, Employee.email == employee.email,
			s3_avatar_file=filename
		)
		await self.session.commit()
		return employee

	async def get_full_profile(self, employee: Employee) -> Employee:
		return await self.__employee_repository.get_record_with_relationships(
			filters=[
				Employee.id == employee.id,
				Employee.email == employee.email
			],
			options=[
				selectinload(Employee.employee_head),
				selectinload(Employee.position),
				selectinload(Employee.department)
			]
		)
