from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends
from fastapi_jsonrpc import Entrypoint
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dependency import AuthenticationDependency
from domain.employee import (
	EmployeeReadSchema, EmployeeRelatedResponse,
	ProfilePhotoResponseDTO,
	EditProfileDTO
)
from domain.employee.service import EmployeeService
from infrastructure.database.model import Employee
from infrastructure.exception import rpc_exceptions
from infrastructure.database.session import async_session_generator
from infrastructure.aws.s3_storage import S3Storage

router = Entrypoint(path='/api/v1/usr', tags=['USER RPC'])
s3 = S3Storage()
employee_service: EmployeeService = EmployeeService()


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
)
async def get_profile(
		employee: Employee = Depends(AuthenticationDependency()),
		session: AsyncSession = Depends(async_session_generator)
) -> EmployeeRelatedResponse:
	"""Профиль текущего пользователя"""
	employee_service.set_async_session(session)
	employee: Employee = await employee_service.get_full_profile(employee.id)
	return EmployeeRelatedResponse.model_validate(
		employee, from_attributes=True)


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
async def get_employee_profile_by_id(
		employee_id: UUID,
		session: AsyncSession = Depends(async_session_generator)
) -> EmployeeRelatedResponse:
	"""Метод для вывода информации пользователя по его ID"""
	employee_service.set_async_session(session)
	employee: Employee = await employee_service.get_full_profile(employee_id)
	return EmployeeRelatedResponse.model_validate(
		employee, from_attributes=True
	)


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
async def get_employee_profile_photo(
		employee_id: UUID,
		session: AsyncSession = Depends(async_session_generator)
) -> ProfilePhotoResponseDTO:
	"""Возвращает ссылку на аватар пользователя по его ID"""
	employee_service.set_async_session(session)
	employee: Employee = await employee_service.get_employee(
		Employee.id == employee_id)
	if not employee:
		raise rpc_exceptions.ObjectDoesNotExistsError(
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
async def update_profile_info(
		edited_info: EditProfileDTO,
		employee: Employee = Depends(AuthenticationDependency()),
		session: AsyncSession = Depends(async_session_generator)
) -> EmployeeReadSchema:
	employee_service.set_async_session(session)
	employee: Employee = await employee_service.update_profile_info(
		employee.id, **edited_info.model_dump())
	return EmployeeReadSchema.model_validate(employee, from_attributes=True)
