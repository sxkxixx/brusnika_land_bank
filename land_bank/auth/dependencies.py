from typing import Annotated, Optional
from fastapi import Header

from .token_service import TokenService
from .models import Employee
from core.rpc_exceptions import AuthorizationError
from layers import EmployeeService, employee_service
from jose import JWTError


class AuthDependency:
    service: EmployeeService = employee_service()

    def __init__(self, is_strict: bool = True):
        self.__is_strict: bool = is_strict

    async def __call__(
            self,
            authorization: Annotated[str, Header()] = None
    ):
        if self.__is_strict:
            return await self.__strict_auth(authorization)
        return await self.__soft_auth(authorization)

    async def __strict_auth(self, access_token: str) -> Employee:
        try:
            payload = TokenService.get_token_payload(access_token)
        except JWTError as error:
            raise AuthorizationError(
                data=f'Access Token has expired. {error.args}')
        employee: Optional[Employee] = await self.service.get_employee(
            Employee.email == payload.get('email')
        )
        if employee is None:
            raise AuthorizationError(data='Access Token is invalid')
        return employee

    async def __soft_auth(
            self,
            access_token: str | None
    ) -> Optional[Employee]:
        if access_token is None:
            return None
        try:
            return await self.__strict_auth(access_token)
        except AuthorizationError:
            return None
