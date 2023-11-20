from datetime import datetime, timedelta
from typing import Annotated

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends, Header, Cookie, Response

from core import Config
from core.rpc_exceptions import AuthorizationError
from .dependencies import AuthDependency
from .models import Employee
from .refresh_session import RefreshSession
from .schemas import EmployeeCreateSchema, EmployeeReadSchema, \
    EmployeeLoginSchema, TokenResponseSchema
from layers import EmployeeService, employee_service
from .token_service import TokenService

auth_application = jsonrpc.Entrypoint(path='/api/v1/auth')


@auth_application.method()
async def register_user(
        user: EmployeeCreateSchema,
        _employee_service: EmployeeService = Depends(employee_service)
) -> EmployeeReadSchema:
    employee: Employee = await _employee_service.create_employee(user)
    return employee.to_schema


@auth_application.method()
async def login_user(
        login_data: EmployeeLoginSchema,
        user_agent: Annotated[str, Header()],
        response: Response,
        _employee_service: EmployeeService = Depends(employee_service)
) -> TokenResponseSchema:
    employee: Employee = await _employee_service.get_login_employee(
        login_data.password,
        Employee.email == login_data.email.lower()
    )
    access_token = TokenService(employee).get_access_token()
    refresh_token = await RefreshSession(employee.id, user_agent).push()
    ttl = int((datetime.now() + timedelta(days=Config.REFRESH_TOKEN_TTL_DAYS)).timestamp())
    response.set_cookie(
        'refresh_token',
        refresh_token,
        expires=ttl,
        max_age=ttl,
        httponly=True
    )
    return TokenResponseSchema(
        access_token=access_token,
    )


@auth_application.method()
async def refresh_session(
        response: Response,
        user_agent: Annotated[str, Header()],
        refresh_token: Annotated[str, Cookie()] = None,
        _employee_service: EmployeeService = Depends(employee_service)
) -> TokenResponseSchema:
    session: RefreshSession = await RefreshSession.get_by_key(refresh_token)
    if session.user_agent != user_agent:
        raise AuthorizationError(data='User-Agent is incorrect')
    await session.delete(refresh_token)
    employee: Employee = await _employee_service.get_employee(
        Employee.id == session.user_id
    )
    access_token = TokenService(employee).get_access_token()
    ttl = int((datetime.now() + timedelta(days=Config.REFRESH_TOKEN_TTL_DAYS)).timestamp())
    refresh_token = await RefreshSession(employee.id, user_agent).push()
    response.set_cookie(
        'refresh_token',
        refresh_token,
        expires=ttl,
        max_age=ttl,
        httponly=True
    )
    return TokenResponseSchema(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@auth_application.method()
async def logout(
        response: Response,
        user_agent: Annotated[str, Header()],
        refresh_token: Annotated[str, Cookie()],
        user: Employee = Depends(AuthDependency())
) -> TokenResponseSchema:
    session = await RefreshSession.get_by_key(refresh_token)
    if session.user_agent != user_agent:
        raise AuthorizationError(data='User-Agent is incorrect')
    if session.user_id != user.id.__str__():
        raise AuthorizationError(data='Refresh Token is stolen')
    await session.delete(refresh_token)
    response.delete_cookie(refresh_token, httponly=True)
    return TokenResponseSchema(
        access_token=None,
        refresh_token_info='Removed from cookie'
    )
