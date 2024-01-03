from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends
from fastapi_jsonrpc import Entrypoint
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dependency import AuthenticationDependency
from domain.employee.schema import (
	EmployeeReadSchema,
	EmployeeRelatedResponse,
	ProfilePhotoResponseDTO,
	EditProfileDTO
)
from infrastructure.database.model import Employee
from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from infrastructure.database.transaction import in_transaction
from infrastructure.exception import rpc_exceptions
from infrastructure.aws.s3_storage import S3Storage
from storage.employee import EmployeeRepository

router = Entrypoint(path='/api/v1/employee', tags=['USER RPC'])
s3 = S3Storage()
employee_repository: EmployeeRepository = EmployeeRepository()


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
)
@in_transaction
async def get_profile(
		employee: Employee = Depends(AuthenticationDependency()),
) -> EmployeeRelatedResponse:
	"""Профиль текущего пользователя"""
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	employee: Employee = await employee_repository.employee_profile(
		session, employee.id
	)
	return EmployeeRelatedResponse.model_validate(
		employee, from_attributes=True)


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
@in_transaction
async def get_employee_profile_by_id(
		employee_id: UUID,
) -> EmployeeRelatedResponse:
	"""Метод для вывода информации пользователя по его ID"""
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	employee: Employee = await employee_repository.employee_profile(
		session, employee_id)
	return EmployeeRelatedResponse.model_validate(
		employee, from_attributes=True
	)


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
@in_transaction
async def get_employee_profile_photo(
		employee_id: UUID,
) -> ProfilePhotoResponseDTO:
	"""Возвращает ссылку на аватар пользователя по его ID"""
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	employee: Employee = await employee_repository.get_employee(
		session, Employee.id == employee_id)
	if not employee:
		raise rpc_exceptions.ObjectNotFoundError(
			data='No user by this UUID'
		)
	if not employee.s3_avatar_file:
		return ProfilePhotoResponseDTO()
	profile_photo_link = await s3.get_pre_signed_url(
		employee.s3_avatar_file)
	return ProfilePhotoResponseDTO(
		profile_photo_link=profile_photo_link,
		expires_in=datetime.utcnow() + timedelta(seconds=3600)
	)


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.TransactionError
	]
)
@in_transaction
async def update_profile_info(
		edited_info: EditProfileDTO,
		employee: Employee = Depends(AuthenticationDependency()),
) -> EmployeeReadSchema:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	employee: Employee = await employee_repository.update_employee(
		session,
		Employee.id == employee.id,
		**edited_info.model_dump()
	)
	return EmployeeReadSchema.model_validate(employee, from_attributes=True)
