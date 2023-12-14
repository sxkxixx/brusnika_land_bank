from auth.model import Employee
from .sqlalchemy_repository import SQLAlchemyRepositoryV1
from bank.model import (
	LandArea,
	Building,
	LandOwner,
	AreaComment,
	ArchiveInfo,
	Status,
	Stage
)

__all__ = [
	'EmployeeRepository',
	'LandAreaRepository',
	'BuildingRepository',
	'LandOwnerRepository',
	'AreaCommentRepository',
	'ArchiveInfoRepository',
	'StatusRepository',
	'StageRepository',
]


class EmployeeRepository(SQLAlchemyRepositoryV1):
	_model = Employee


class LandAreaRepository(SQLAlchemyRepositoryV1):
	_model = LandArea


class BuildingRepository(SQLAlchemyRepositoryV1):
	_model = Building


class LandOwnerRepository(SQLAlchemyRepositoryV1):
	_model = LandOwner


class AreaCommentRepository(SQLAlchemyRepositoryV1):
	_model = AreaComment


class ArchiveInfoRepository(SQLAlchemyRepositoryV1):
	_model = ArchiveInfo


class StatusRepository(SQLAlchemyRepositoryV1):
	_model = Status


class StageRepository(SQLAlchemyRepositoryV1):
	_model = Stage
