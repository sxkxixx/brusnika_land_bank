from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from domain.employee.schema import ProfilePhotoResponseDTO
from application.auth.dependency import AuthenticationDependency
from application.file.file_validator import FileValidator
from domain.employee.service import EmployeeService
from infrastructure.aws.s3_storage import S3Storage
from infrastructure.database.model import Employee
from infrastructure.database.session import async_session_generator
from infrastructure.exception import rpc_exceptions
from datetime import datetime, timedelta

router = APIRouter(prefix='/rest/api/v1/usr', tags=['USER REST'])

file_validator: FileValidator = FileValidator()
s3_service: S3Storage = S3Storage()
employee_service: EmployeeService = EmployeeService()


@router.post('/set_profile_avatar')
async def set_employee_photo(
		employee: Employee = Depends(AuthenticationDependency()),
		file: UploadFile = File(...),  # type(file) -> UploadFile,
		session: AsyncSession = Depends(async_session_generator)
) -> ProfilePhotoResponseDTO:
	"""
	<b>REST - запрос</b>
	JPG, JPEG, PNG - доступные для установки форматы,
	если файл побит - выпадет ошибка.
	Если у пользователя уже установлен файл, произойдет его замена
	"""
	if not await file_validator.is_valid_file(file):
		raise HTTPException(status_code=400, detail='File signature is not valid')
	employee_service.set_async_session(session)
	if employee.s3_avatar_file:
		await s3_service.delete_file(employee.s3_avatar_file)
	file_name = await s3_service.upload_file(file)
	await employee_service.set_employee_photo(employee, file_name)
	pre_signed_url = await s3_service.get_pre_signed_url(file_name=file_name)
	return ProfilePhotoResponseDTO(
		profile_photo_link=pre_signed_url,
		expires_in=datetime.utcnow() + timedelta(seconds=3600)
	)
