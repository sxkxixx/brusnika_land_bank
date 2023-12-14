from sqlalchemy.ext.asyncio import AsyncSession

from core import get_async_session
from .service import *
from fastapi import Depends

__all__ = [
    'EmployeeService',
    'employee_service',
    'land_area_service',
    'LandAreaService'
]


def employee_service(session: AsyncSession = Depends(get_async_session)) -> EmployeeService:
    return EmployeeService(session)


def land_area_service(session: AsyncSession = Depends(get_async_session)) -> LandAreaService:
    return LandAreaService(session)
