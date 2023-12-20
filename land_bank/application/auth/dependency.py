from typing import Annotated, Optional
from fastapi import Header

from domain.employee.service import EmployeeService
from .token import TokenService
from infrastructure.database.model import Employee
from infrastructure.database.session import async_session
from infrastructure.exception import rpc_exceptions
from jose import JWTError

__all__ = [
	'AuthenticationDependency',
	'AuthorizationDependency'
]


def _get_token_payload(access_token: str) -> dict:
	try:
		payload = TokenService.get_token_payload(access_token)
	except JWTError as error:
		raise rpc_exceptions.AuthenticationError(
			data=f'Access Token has expired. {error.args}')
	return payload


class AuthenticationDependency:
	def __init__(self, is_strict: bool = True):
		self.__is_strict: bool = is_strict
		self.__employee_service: EmployeeService = EmployeeService(async_session())

	async def __call__(
			self,
			authorization: Annotated[str, Header()] = None
	):
		if self.__is_strict:
			return await self.__strict_auth(authorization)
		return await self.__soft_auth(authorization)

	async def __strict_auth(
			self,
			access_token: str,
	) -> Employee:
		payload = _get_token_payload(access_token)
		employee: Optional[
			Employee] = await self.__employee_service.get_employee(
			Employee.email == payload.get('email'))
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
		self.__service: EmployeeService = EmployeeService(async_session())

	async def __call__(
			self,
			authorization: Annotated[str, Header()] = None,
	):
		payload = _get_token_payload(authorization)
		employee: Employee = await (
			self.__service.get_employee_with_permissions(
				Employee.email == payload.get('email')))
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
