from sqlalchemy.exc import IntegrityError
from typing import Type, Union, Dict, Optional
from pydantic import BaseModel
from sqlalchemy.orm import selectinload

from layers.repositories import BaseRepository, SQLAlchemyRepositoryV1
from core.rpc_exceptions import UniqueEmailError, LoginError
from auth.models import Employee

from utils import Hasher


class EmployeeService:
    def __init__(
            self,
            repository: Type[Union[BaseRepository, SQLAlchemyRepositoryV1]]
    ):
        self.repository = repository()

    async def create_employee(self, data: Union[Dict, BaseModel]) -> Employee:
        if isinstance(data, BaseModel):
            data: Dict = data.model_dump()
        try:
            employee: Employee = await self.repository.create_record(
                email=data.get('email'),
                hashed_password=Hasher.get_password_hash(
                    data.get('password')),
                last_name=data.get('last_name'),
                first_name=data.get('first_name'),
                patronymic=data.get('patronymic'),
                phone_number=data.get('phone_number'),
            )
        except IntegrityError:
            raise UniqueEmailError()
        return employee

    async def get_login_employee(
            self,
            password: str,
            *filters
    ) -> Employee:
        employee: Employee = await self.repository.get_record(*filters)
        if employee is None:
            raise LoginError(data='User is missed')
        if not Hasher.verify_password(password, employee.hashed_password):
            raise LoginError(data='Incorrect password')
        return employee

    async def get_employee(self, *filters) -> Optional[Employee]:
        employee: Employee = await self.repository.get_record(*filters)
        if employee is None:
            return None
        return employee

    async def get_with_position(self, *filters) -> Optional[Employee]:
        employee: Employee = await self.repository.get_record_with_relationships(
            filters=filters, options=[selectinload(Employee.position)]
        )
        if employee is None:
            return None
        return employee

    async def set_employee_photo(
            self,
            employee: Employee,
            filename: str
    ) -> Employee:
        return await self.repository.update_record(
            Employee.id == employee.id, Employee.email == employee.email,
            s3_avatar_file=filename
        )

    async def get_full_profile(self, employee: Employee) -> Employee:
        return await self.repository.get_record_with_relationships(
            filters=[
                Employee.id == employee.id,
                Employee.email == employee.email
            ],
            options=[
                selectinload(Employee.employee_head),
                selectinload(Employee.position),
                selectinload(Employee.department)
            ]
        )
