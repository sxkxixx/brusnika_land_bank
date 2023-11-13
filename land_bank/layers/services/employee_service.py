from sqlalchemy.exc import IntegrityError
from typing import Type, Union, Dict, Optional
from pydantic import BaseModel

from layers.repositories import BaseRepository, SQLAlchemyRepository
from core.rpc_exceptions import UniqueEmailError, LoginError
from auth.models import Employee

from core import async_session
from utils import Hasher


class EmployeeService:
    def __init__(
            self,
            repository: Type[Union[BaseRepository, SQLAlchemyRepository]]
    ):
        session = async_session()
        self.repository = repository(session)

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
                tg_username=data.get('tg_username'),
            )
            await self.repository.commit()
        except IntegrityError:
            await self.repository.rollback()
            raise UniqueEmailError()
        return employee

    async def get_login_employee(
            self,
            password: str,
            *filters
    ) -> Employee:
        employee: Employee = self.repository.get_record(*filters)
        if employee is None:
            raise LoginError(data='User is missed')
        if not Hasher.verify_password(password, employee.hashed_password):
            raise LoginError(data='Incorrect password')
        return employee

    async def get_employee(self, *filters) -> Optional[Employee]:
        employee: Employee = self.repository.get_record(*filters)
        if employee is None:
            return None
        return employee


