from auth.models import Employee
from .sqlalchemy_repository import SQLAlchemyRepositoryV1

__all__ = [
    'EmployeeRepository'
]


class EmployeeRepository(SQLAlchemyRepositoryV1):
    _model = Employee
