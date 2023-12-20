from datetime import datetime, timedelta
from typing import Annotated
import fastapi_jsonrpc as jsonrpc
from fastapi import Depends, Header, Cookie, Response
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dependency import AuthenticationDependency
from application.auth.refresh import RefreshSession
from application.auth.token import TokenService
from domain.employee import *
from domain.employee.service import EmployeeService
from domain.token import *
from infrastructure.database.model import Employee
from infrastructure.database.session import async_session_generator
from infrastructure.exception import rpc_exceptions
from infrastructure.settings import AppSettings

router = jsonrpc.Entrypoint(path='/api/v1/auth')


@router.method(errors=[rpc_exceptions.UniqueEmailError])
async def register_user(
		user: EmployeeCreateSchema,
		session: AsyncSession = Depends(async_session_generator)
) -> EmployeeReadSchema:
	employee_service: EmployeeService = EmployeeService(session)
	employee: Employee = await employee_service.create_employee(
		**user.model_dump())
	return EmployeeReadSchema.model_validate(employee, from_attributes=True)


@router.method(errors=[rpc_exceptions.LoginError])
async def login_user(
		login_data: EmployeeLoginSchema,
		user_agent: Annotated[str, Header()],
		response: Response,
		session: AsyncSession = Depends(async_session_generator),
) -> TokenResponseSchema:
	employee_service: EmployeeService = EmployeeService(session)
	employee: Employee = await employee_service.get_login_employee(
		login_data.password,
		Employee.email == login_data.email.lower()
	)
	access_token = TokenService(employee).get_access_token()
	refresh_token = await RefreshSession(employee.id, user_agent).push()
	ttl = int((datetime.now() + timedelta(
		days=AppSettings.REFRESH_TOKEN_TTL_DAYS)).timestamp())
	response.set_cookie(
		'refresh_token',
		refresh_token,
		expires=ttl,
		max_age=ttl,
		httponly=True
	)
	return TokenResponseSchema(access_token=access_token)


@router.method(errors=[rpc_exceptions.AuthenticationError])
async def refresh_session(
		response: Response,
		user_agent: Annotated[str, Header()],
		refresh_token: Annotated[str, Cookie()] = None,
		database_session: AsyncSession = Depends(async_session_generator),
) -> TokenResponseSchema:
	employee_service: EmployeeService = EmployeeService(database_session)
	employee_session: RefreshSession = await RefreshSession.get_by_key(
		refresh_token)
	if employee_session.user_agent != user_agent:
		raise rpc_exceptions.AuthenticationError(
			data='User-Agent is incorrect')
	await employee_session.delete(refresh_token)
	employee: Employee = await employee_service.get_employee(
		Employee.id == employee_session.user_id
	)
	access_token = TokenService(employee).get_access_token()
	ttl = int((datetime.now() + timedelta(
		days=AppSettings.REFRESH_TOKEN_TTL_DAYS)).timestamp())
	refresh_token = await RefreshSession(employee.id, user_agent).push()
	response.set_cookie(
		'refresh_token',
		refresh_token,
		expires=ttl,
		max_age=ttl,
		httponly=True
	)
	return TokenResponseSchema(access_token=access_token)


@router.method(errors=[rpc_exceptions.AuthenticationError])
async def logout(
		response: Response,
		user_agent: Annotated[str, Header()],
		refresh_token: Annotated[str, Cookie()],
		user: Employee = Depends(AuthenticationDependency()),
) -> TokenResponseSchema:
	employee_session = await RefreshSession.get_by_key(refresh_token)
	if employee_session.user_agent != user_agent:
		raise rpc_exceptions.AuthenticationError(
			data='User-Agent is incorrect')
	if employee_session.user_id != user.id.__str__():
		raise rpc_exceptions.AuthenticationError(
			data='Refresh Token is stolen')
	await employee_session.delete(refresh_token)
	response.delete_cookie(refresh_token, httponly=True)
	return TokenResponseSchema(access_token=None)


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
	description="Возвращает полную информацию о текущем пользователе"
)
async def get_employee_profile_info(
		employee: Employee = Depends(AuthenticationDependency()),
		session: AsyncSession = Depends(async_session_generator),
) -> EmployeeRelationsResponse:
	employee_service: EmployeeService = EmployeeService(session)
	employee: Employee = await employee_service.get_full_profile(employee)
	return EmployeeRelationsResponse.from_model(employee)
