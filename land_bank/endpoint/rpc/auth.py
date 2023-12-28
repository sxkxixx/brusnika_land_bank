from typing import Annotated, Optional
import fastapi_jsonrpc as jsonrpc
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Header, Cookie, Response

from application.auth.hasher import Hasher
from application.message import PasswordResetMessage
from application.auth.token import TokenService
from application.auth.refresh import RefreshSession
from application.auth.dependency import AuthenticationDependency
from domain.token import *
from domain.employee import *
from domain.email_message.schemas import *
from domain.employee.service import EmployeeService
from infrastructure.celery import send_message
from infrastructure.redis import RedisService
from infrastructure.settings import AppSettings
from infrastructure.database.model import Employee
from infrastructure.exception import rpc_exceptions
from infrastructure.database.transaction import in_transaction
from infrastructure.database.session import async_session_generator

from domain.employee.repository import EmployeeRepository

router = jsonrpc.Entrypoint(path='/api/v1/auth', tags=['AUTH'])
employee_service: EmployeeService = EmployeeService()
redis_service = RedisService()


def repository_dependency() -> EmployeeRepository:
	return EmployeeRepository()


@router.method(errors=[rpc_exceptions.UniqueEmailError])
@in_transaction
async def register_user(
		user: EmployeeCreateSchema,
		employee_repository: EmployeeRepository = Depends(repository_dependency)
) -> EmployeeReadSchema:
	employee: Employee = await employee_repository.create_user(
		**user.model_dump())
	return EmployeeReadSchema.model_validate(employee, from_attributes=True)


@router.method(errors=[rpc_exceptions.LoginError])
@in_transaction
async def login_user(
		data: EmployeeLoginSchema,
		user_agent: Annotated[str, Header()],
		response: Response,
) -> TokenResponseSchema:
	employee_repository = EmployeeRepository()
	try:
		employee: Employee = await employee_repository.get_employee(
			Employee.email == data.email)
	except rpc_exceptions.ObjectDoesNotExistsError:
		raise rpc_exceptions.LoginError(data="User does not exist")
	if not Hasher.verify_password(data.password, employee.hashed_password):
		raise rpc_exceptions.LoginError(data="Incorrect password")
	access_token = TokenService(employee).get_access_token()
	_refresh_session = RefreshSession(employee.id, user_agent)
	refresh_token = await redis_service.setex_entity(_refresh_session)
	expires = int((datetime.now() + _refresh_session.time_to_leave()).timestamp())
	response.set_cookie(
		'refresh_token', refresh_token, expires=expires,
		httponly=True, path='/api/v1/auth'
	)
	return TokenResponseSchema(access_token=access_token)


@router.method(errors=[rpc_exceptions.AuthenticationError])
async def refresh_session(
		response: Response,
		user_agent: Annotated[str, Header()],
		refresh_token: Annotated[str, Cookie()],
		employee_repository: EmployeeRepository = Depends(repository_dependency),
) -> TokenResponseSchema:
	session: Optional[RefreshSession] = await redis_service.get_by_key(
		refresh_token, RefreshSession)
	if not session:
		raise rpc_exceptions.AuthenticationError(
			data='Session has expired, login again')
	if session.user_agent != user_agent:
		raise rpc_exceptions.AuthenticationError(
			data='User-Agent is incorrect')
	await redis_service.delete_by_key(refresh_token)
	employee: Employee = await employee_repository.get_employee(Employee.id == session.user_id)
	if not employee:
		raise rpc_exceptions.AuthenticationError(
			data='User not exists by this refresh token')
	access_token = TokenService(employee).get_access_token()
	session = RefreshSession(employee.id, user_agent)
	refresh_token: str = await redis_service.setex_entity(session)
	expires = int((datetime.now() + session.time_to_leave()).timestamp())
	response.set_cookie(
		'refresh_token', refresh_token, expires=expires,
		httponly=True, path='/api/v1/auth'
	)
	return TokenResponseSchema(access_token=access_token)


@router.method(errors=[rpc_exceptions.AuthenticationError])
async def logout(
		response: Response,
		user_agent: Annotated[str, Header()],
		refresh_token: Annotated[str, Cookie()],
		user: Employee = Depends(AuthenticationDependency()),
) -> TokenResponseSchema:
	session: Optional[RefreshSession] = await redis_service.get_by_key(
		refresh_token, RefreshSession)
	if not session:
		raise rpc_exceptions.AuthenticationError(data='Already logouted')
	if session.user_agent != user_agent:
		raise rpc_exceptions.AuthenticationError(
			data='User-Agent is incorrect')
	if session.user_id != user.id.__str__():
		raise rpc_exceptions.AuthenticationError(
			data='Refresh Token is stolen')
	await redis_service.delete_by_key(refresh_token)
	response.delete_cookie(refresh_token, httponly=True)
	return TokenResponseSchema(access_token=None)


@router.method(errors=[rpc_exceptions.AuthenticationError])
async def get_password_reset_email_message(
		data: PasswordResetRequestDTO,
		session: AsyncSession = Depends(async_session_generator)
) -> PasswordResetResponseDTO:
	employee_service.set_async_session(session)
	employee: Employee = await employee_service.get_employee(
		Employee.email == data.email
	)
	if not employee:
		raise rpc_exceptions.ObjectDoesNotExistsError(
			'No user by this email not exists'
		)
	message = PasswordResetMessage(
		sender='', receiver=employee.email, user_email=employee.email)
	send_message.delay(message)
	return PasswordResetResponseDTO(email=employee.email)
