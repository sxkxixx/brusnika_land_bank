from typing import Annotated, Optional
import fastapi_jsonrpc as jsonrpc
from datetime import datetime
from fastapi import Depends, Header, Cookie, Response
from application.auth import (
	Hasher,
	TokenService,
	RefreshSession,
	AuthenticationDependency
)
from application.message import PasswordResetMessage

from domain.token import TokenResponseSchema
from domain.employee import *
from domain.email_message.schemas import *
from domain.employee.repository import EmployeeRepository

from infrastructure.celery import send_message
from infrastructure.redis import RedisService
from infrastructure.database.model import Employee
from infrastructure.exception import rpc_exceptions


router = jsonrpc.Entrypoint(path='/api/v1/auth', tags=['AUTH'])
redis_service = RedisService()
employee_repository: EmployeeRepository = EmployeeRepository()


@router.method(errors=[rpc_exceptions.UniqueEmailError])
async def register_user(
		user: EmployeeCreateSchema,
) -> EmployeeReadSchema:
	employee: Employee = await employee_repository.create_user(
		**user.model_dump())
	return EmployeeReadSchema.model_validate(employee, from_attributes=True)


@router.method(errors=[rpc_exceptions.LoginError])
async def login_user(
		data: EmployeeLoginSchema,
		user_agent: Annotated[str, Header()],
		response: Response,
) -> TokenResponseSchema:
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
	expires = int(
		(datetime.now() + _refresh_session.time_to_leave()).timestamp())
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
) -> TokenResponseSchema:
	session: Optional[RefreshSession] = await redis_service.get_by_key(
		refresh_token, RefreshSession)
	if not session:
		raise rpc_exceptions.AuthenticationError(
			data='Session has expired, login again')
	if session.user_agent != user_agent:
		raise rpc_exceptions.AuthenticationError(
			data='User-Agent is incorrect')
	employee: Employee = await employee_repository.get_employee(
		Employee.id == session.user_id)
	if not employee:
		raise rpc_exceptions.AuthenticationError(
			data='User not exists by this refresh token')
	await redis_service.delete_by_key(refresh_token)
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
		raise rpc_exceptions.AuthenticationError(data='Already logout')
	if session.user_agent != user_agent:
		raise rpc_exceptions.AuthenticationError(
			data='User-Agent is incorrect')
	if session.user_id != str(user.id):
		raise rpc_exceptions.AuthenticationError(
			data='Refresh Token is stolen')
	await redis_service.delete_by_key(refresh_token)
	response.delete_cookie(refresh_token, httponly=True)
	return TokenResponseSchema(access_token=None)


@router.method(errors=[rpc_exceptions.AuthenticationError])
async def get_password_reset_email_message(
		data: PasswordResetRequestDTO,
) -> PasswordResetResponseDTO:
	employee: Employee = await employee_repository.get_employee(
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
