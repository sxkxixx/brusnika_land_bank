from auth.models import Employee
from .sqlalchemy_repository import SQLAlchemyRepository

__all__ = [
    'EmployeeRepository'
]


class EmployeeRepository(SQLAlchemyRepository):
    _model = Employee
