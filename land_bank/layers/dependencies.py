from .services import *
from .repositories import *

__all__ = [
    'EmployeeService',
    'employee_service'
]


def employee_service() -> EmployeeService:
    return EmployeeService(EmployeeRepository)
