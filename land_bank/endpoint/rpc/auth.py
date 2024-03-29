from datetime import datetime
from typing import Annotated, Optional

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends, Header, Cookie, Response
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth import (
    Hasher,
    TokenService,
    RefreshSession,
    AuthenticationDependency
)
from application.message import PasswordResetMessage
from domain.email_message.schemas import (
    PasswordResetRequestDTO, PasswordResetResponseDTO
)
from domain.employee.schema import (
    EmployeeCreateSchema, EmployeeReadSchema, EmployeeLoginSchema,
)
from domain.token import TokenResponseSchema
from infrastructure.celery import send_message
from infrastructure.database.model import Employee
from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from infrastructure.database.transaction import in_transaction
from infrastructure.exception import rpc_exceptions
from infrastructure.redis import RedisService
from storage.employee import EmployeeRepository

router = jsonrpc.Entrypoint(path='/api/v1/auth', tags=['AUTH'])
redis_service = RedisService()
employee_repository: EmployeeRepository = EmployeeRepository()


@router.method(errors=[rpc_exceptions.UniqueEmailError])
@in_transaction
async def register_user(
        user: EmployeeCreateSchema,
) -> EmployeeReadSchema:
    session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    employee: Employee = await employee_repository.create_user(
        session, **user.model_dump())
    return EmployeeReadSchema.model_validate(employee, from_attributes=True)


@router.method(errors=[rpc_exceptions.LoginError])
@in_transaction
async def login_user(
        data: EmployeeLoginSchema,
        user_agent: Annotated[str, Header()],
        response: Response,
) -> TokenResponseSchema:
    try:
        session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
        employee: Employee = await employee_repository.get_employee(
            session, Employee.email == data.email)
    except rpc_exceptions.ObjectNotFoundError:
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
@in_transaction
async def refresh_session(
        response: Response,
        user_agent: Annotated[str, Header()],
        refresh_token: Annotated[str, Cookie()],
) -> TokenResponseSchema:
    session: Optional[RefreshSession] = await redis_service.get_by_key(
        # type: ignore
        refresh_token, RefreshSession)
    if not session:
        raise rpc_exceptions.AuthenticationError(
            data='Session has expired, login again')
    if session.user_agent != user_agent:
        raise rpc_exceptions.AuthenticationError(
            data='User-Agent is incorrect')
    async_db_session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    employee: Employee = await employee_repository.get_employee(
        async_db_session, Employee.id == session.user_id)
    if not employee:
        raise rpc_exceptions.AuthenticationError(
            data='User not exists by this refresh token')
    await redis_service.delete_by_key(refresh_token)
    access_token = TokenService(employee).get_access_token()
    session = RefreshSession(employee.id, user_agent)
    updated_refresh_token: str = await redis_service.setex_entity(session)
    expires = int((datetime.now() + session.time_to_leave()).timestamp())
    response.set_cookie(
        'refresh_token', updated_refresh_token, expires=expires,
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
        # type: ignore
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
@in_transaction
async def get_password_reset_email_message(
        data: PasswordResetRequestDTO,
) -> PasswordResetResponseDTO:
    session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    employee: Employee = await employee_repository.get_employee(
        session, Employee.email == data.email
    )
    if not employee:
        raise rpc_exceptions.ObjectNotFoundError(
            'No user by this email not exists'
        )
    message = PasswordResetMessage(
        sender='', receiver=employee.email, user_email=employee.email)
    send_message.delay(message)
    return PasswordResetResponseDTO(email=employee.email)
