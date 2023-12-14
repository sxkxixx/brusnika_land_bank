from datetime import datetime, timedelta
from typing import Annotated

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends, Header, Cookie, Response, File, UploadFile

from core import Config
from core import rpc_exceptions
from util import FileValidator
from .schema import (
	EmployeeCreateSchema,
	EmployeeReadSchema,
	EmployeeLoginSchema,
	TokenResponseSchema,
	EmployeeRelationsResponse
)
from .dependency import AuthenticationDependency, AuthorizationDependency
from .model import Employee
from .refresh_session import RefreshSession
from layer import EmployeeService, employee_service, S3Service
from .token_service import TokenService

auth_application = jsonrpc.Entrypoint(path='/api/v1/auth')
s3_service = S3Service()
file_validator = FileValidator()


@auth_application.method(errors=[rpc_exceptions.UniqueEmailError])
async def register_user(
		user: EmployeeCreateSchema,
		_employee_service: EmployeeService = Depends(employee_service)
) -> EmployeeReadSchema:
	employee: Employee = await _employee_service.create_employee(user)
	return EmployeeReadSchema.model_validate(employee, from_attributes=True)


@auth_application.method(errors=[rpc_exceptions.LoginError])
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
	ttl = int((datetime.now() + timedelta(
		days=Config.REFRESH_TOKEN_TTL_DAYS)).timestamp())
	response.set_cookie('refresh_token', refresh_token,
						expires=ttl, max_age=ttl, httponly=True)
	return TokenResponseSchema(access_token=access_token)


@auth_application.method(errors=[rpc_exceptions.AuthenticationError])
async def refresh_session(
		response: Response,
		user_agent: Annotated[str, Header()],
		refresh_token: Annotated[str, Cookie()] = None,
		_employee_service: EmployeeService = Depends(employee_service)
) -> TokenResponseSchema:
	session: RefreshSession = await RefreshSession.get_by_key(refresh_token)
	if session.user_agent != user_agent:
		raise rpc_exceptions.AuthenticationError(data='User-Agent is '
													  'incorrect')
	await session.delete(refresh_token)
	employee: Employee = await _employee_service.get_employee(
		Employee.id == session.user_id
	)
	access_token = TokenService(employee).get_access_token()
	ttl = int((datetime.now() + timedelta(
		days=Config.REFRESH_TOKEN_TTL_DAYS)).timestamp())
	refresh_token = await RefreshSession(employee.id, user_agent).push()
	response.set_cookie(
		'refresh_token',
		refresh_token,
		expires=ttl,
		max_age=ttl,
		httponly=True
	)
	return TokenResponseSchema(access_token=access_token)


@auth_application.method(errors=[rpc_exceptions.AuthenticationError])
async def logout(
		response: Response,
		user_agent: Annotated[str, Header()],
		refresh_token: Annotated[str, Cookie()],
		user: Employee = Depends(AuthenticationDependency())
) -> TokenResponseSchema:
	session = await RefreshSession.get_by_key(refresh_token)
	if session.user_agent != user_agent:
		raise rpc_exceptions.AuthenticationError(data='User-Agent is '
													  'incorrect')
	if session.user_id != user.id.__str__():
		raise rpc_exceptions.AuthenticationError(data='Refresh Token is '
													  'stolen')
	await session.delete(refresh_token)
	response.delete_cookie(refresh_token, httponly=True)
	return TokenResponseSchema(access_token=None)


@auth_application.method(
	errors=[rpc_exceptions.AuthenticationError],
	description="Возвращает полную информацию о текущем пользователе"
)
async def get_employee_profile_info(
		employee: Employee = Depends(AuthenticationDependency()),
		_employee_service: EmployeeService = Depends(employee_service)
) -> EmployeeRelationsResponse:
	employee: Employee = await _employee_service.get_full_profile(employee)
	return EmployeeRelationsResponse.from_model(employee)


@auth_application.post(
	'/api/v1/upload_user_avatar',
	description="REST-запрос, передача с помощью JavaScript FormData или аналога в TS"
)
async def set_employee_photo(
		employee: Employee = Depends(AuthenticationDependency()),
		_employee_service: EmployeeService = Depends(employee_service),
		file: UploadFile = File(...),  # type(file) -> UploadFile
) -> jsonrpc.JsonRpcResponse:
	if not await file_validator.is_valid_file(file):
		raise rpc_exceptions.ValidationFileError()
	file_name = await s3_service.upload_file(file)
	await _employee_service.set_employee_photo(employee, file_name)
	pre_signed_url = await s3_service.get_pre_signed_url(file_name=file_name)
	response = jsonrpc.JsonRpcResponse(result={
		'employee_avatar_link': pre_signed_url
	})
	return response
