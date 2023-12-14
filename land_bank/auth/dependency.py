from typing import Annotated, Optional
from fastapi import Header, Depends

from .token_service import TokenService
from .model import Employee
from core.rpc_exceptions import AuthenticationError, AuthorizationError
from layer import EmployeeService, employee_service
from jose import JWTError


class EmployeeDependency:
	def get_token_payload(self, access_token: str) -> dict:
		try:
			payload = TokenService.get_token_payload(access_token)
		except JWTError as error:
			raise AuthenticationError(
				data=f'Access Token has expired. {error.args}')
		return payload


class AuthenticationDependency(EmployeeDependency):
	def __init__(self, is_strict: bool = True):
		self.__is_strict: bool = is_strict

	async def __call__(
			self,
			authorization: Annotated[str, Header()] = None,
			service: EmployeeService = Depends(employee_service)
	):
		if self.__is_strict:
			return await self.__strict_auth(authorization, service)
		return await self.__soft_auth(authorization)

	async def __strict_auth(
			self,
			access_token: str,
			service: EmployeeService
	) -> Employee:
		payload = self.get_token_payload(access_token)
		employee: Optional[Employee] = await service.get_employee(
			Employee.email == payload.get('email'))
		if employee is None:
			raise AuthenticationError(data='Access Token is invalid')
		return employee

	async def __soft_auth(
			self,
			access_token: str | None
	) -> Optional[Employee]:
		if access_token is None:
			return None
		try:
			return await self.__strict_auth(access_token)
		except AuthenticationError:
			return None


class AuthorizationDependency(EmployeeDependency):
	def __init__(self, permission_name: str):
		self.__permission_name = permission_name

	async def __call__(
			self,
			authorization: Annotated[str, Header()] = None,
			service: EmployeeService = Depends(employee_service),
	):
		payload = self.get_token_payload(authorization)
		employee: Employee = await service.get_employee_with_permissions(
			Employee.email == payload.get('email'))
		if employee is None:
			raise AuthenticationError(data='Access Token is invalid')
		if not await self.__check_permissions(employee):
			raise AuthorizationError(data=f"Forbidden for current employee")
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
