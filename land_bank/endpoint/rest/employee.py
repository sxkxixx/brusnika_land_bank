from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from domain.employee.schema import ProfilePhotoResponseDTO
from application.auth.dependency import AuthenticationDependency
from application.file.file_validator import FileValidator
from infrastructure.aws.s3_storage import S3Storage
from infrastructure.database.model import Employee
from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from infrastructure.database.transaction import in_transaction
from storage.employee import EmployeeRepository

router = APIRouter(prefix='/rest/api/v1/employee', tags=['USER REST'])

file_validator: FileValidator = FileValidator()
s3_service: S3Storage = S3Storage()
employee_repository: EmployeeRepository = EmployeeRepository()


@router.post('/set_profile_avatar')
@in_transaction
async def set_employee_photo(
		employee: Employee = Depends(AuthenticationDependency()),
		file: UploadFile = File(...),  # type(file) -> UploadFile,
) -> ProfilePhotoResponseDTO:
	"""
	<b>REST - запрос</b>
	JPG, JPEG, PNG - доступные для установки форматы,
	если файл побит - выпадет ошибка.
	Если у пользователя уже установлен файл, произойдет его замена
	"""
	if not await file_validator.is_valid_file(file):
		raise HTTPException(
			status_code=400, detail='File signature is not valid')
	if employee.s3_avatar_file:
		await s3_service.delete_file(employee.s3_avatar_file)
	file_name = await s3_service.upload_file(file)
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	await employee_repository.update_employee(
		session,
		Employee.id == employee.id, Employee.email == Employee.email,
		s3_avatar_file=file_name
	)
	pre_signed_url = await s3_service.get_pre_signed_url(file_name=file_name)
	return ProfilePhotoResponseDTO(
		profile_photo_link=pre_signed_url,
		expires_in=datetime.utcnow() + timedelta(seconds=3600)
	)
