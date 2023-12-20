from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dependency import AuthenticationDependency
from application.file.file_validator import FileValidator
from domain.employee.service import EmployeeService
from infrastructure.aws.s3_storage import S3Storage
from infrastructure.database.model import Employee
from infrastructure.database.session import async_session_generator
from infrastructure.exception import rpc_exceptions

router = APIRouter(prefix='/api/v1/employee', tags=['REST'])

file_validator: FileValidator = FileValidator()
s3_service: S3Storage = S3Storage()


@router.post('/set_profile_avatar', tags=['EMPLOYEE'])
async def set_employee_photo(
		employee: Employee = Depends(AuthenticationDependency()),
		file: UploadFile = File(...),  # type(file) -> UploadFile,
		session: AsyncSession = Depends(async_session_generator)
):
	employee_service: EmployeeService = EmployeeService(session)
	if not await file_validator.is_valid_file(file):
		raise rpc_exceptions.ValidationFileError()
	file_name = await s3_service.upload_file(file)
	await employee_service.set_employee_photo(employee, file_name)
	pre_signed_url = await s3_service.get_pre_signed_url(file_name=file_name)
	return pre_signed_url
