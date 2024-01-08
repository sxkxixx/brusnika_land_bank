from typing import Annotated, Dict, Optional
from fastapi import Header
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from infrastructure.database.transaction import in_transaction
from storage.employee import EmployeeRepository
from .token import TokenService
from infrastructure.database.model import Employee
from infrastructure.exception import rpc_exceptions

__all__ = [
	'AuthenticationDependency',
	'AuthorizationDependency'
]


def _get_token_payload(access_token: str) -> Dict:
	try:
		payload: Dict = TokenService.get_token_payload(access_token)
	except JWTError as error:
		raise rpc_exceptions.AuthenticationError(
			data=f'Access Token has expired. {error.args}')
	return payload


class AuthenticationDependency:
	def __init__(self, is_strict: bool = True):
		self.__is_strict: bool = is_strict
		self.__repository: EmployeeRepository = EmployeeRepository()

	async def __call__(
			self,
			authorization: Annotated[str, Header()]
	):
		if self.__is_strict:
			return await self.__strict_auth(authorization)
		return await self.__soft_auth(authorization)

	@in_transaction
	async def __strict_auth(
			self,
			access_token: str,
	) -> Employee:
		if not access_token:
			raise rpc_exceptions.AuthenticationError(
				data='No access token there')
		payload = _get_token_payload(access_token)
		employee: Optional[Employee] = await self.__repository.get_employee(
			ASYNC_CONTEXT_SESSION.get(), Employee.email == payload.get('email')
		)
		if employee is None:
			raise rpc_exceptions.AuthenticationError(
				data='Access Token is invalid')
		return employee

	async def __soft_auth(
			self,
			access_token: str | None,
	) -> Optional[Employee]:
		if access_token is None:
			return None
		try:
			return await self.__strict_auth(access_token)
		except rpc_exceptions.AuthenticationError:
			return None


class AuthorizationDependency:
	def __init__(self, permission_name: str):
		self.__permission_name = permission_name
		self.__employee_repository: EmployeeRepository = EmployeeRepository()

	@in_transaction
	async def __call__(
			self,
			authorization: Optional[Annotated[str, Header()]] = None,
	):
		if not authorization:
			raise rpc_exceptions.AuthenticationError(
				data='No access token there'
			)
		payload: Dict = _get_token_payload(authorization)
		session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
		employee: Optional[Employee] = await (
			self.__employee_repository.get_employee_with_permissions(
				session, Employee.email == payload.get('email')))
		if employee is None:
			raise rpc_exceptions.AuthenticationError(
				data='Access Token is invalid')
		if not await self.__check_permissions(employee):
			raise rpc_exceptions.AuthorizationError(
				data=f"Forbidden for current employee")
		return employee

	async def __check_permissions(self, employee: Employee) -> bool:
		has_perm = False
		employee_permissions = employee.position.permissions
		for permission_position in employee_permissions:
			permission_name = permission_position.permission.permission_name
			if permission_name == self.__permission_name:
				has_perm = True
				break
		return has_perm
