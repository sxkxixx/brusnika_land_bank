from datetime import datetime
from typing import List, Optional, TypeVar

import sqlalchemy
from uuid import UUID, uuid4
from sqlalchemy import MetaData
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

meta = MetaData()


class Base(DeclarativeBase):
	meta = meta

	id: Mapped[UUID] = mapped_column(
		sqlalchemy.UUID, primary_key=True, default=uuid4
	)


DatabaseEntity = TypeVar('DatabaseEntity', bound=Base)


class Employee(Base):
	"""
	Модель данных: "Сотрудник Земельного Банка"
	"""
	__tablename__ = 'land_bank_employee'

	email: Mapped[str] = mapped_column(
		sqlalchemy.String(length=64),
		nullable=False, unique=True, index=True
	)
	hashed_password: Mapped[str] = mapped_column(
		sqlalchemy.String(length=128), nullable=False
	)
	last_name: Mapped[str] = mapped_column(
		sqlalchemy.String(32), nullable=False
	)
	first_name: Mapped[str] = mapped_column(
		sqlalchemy.String(32), nullable=False
	)
	patronymic: Mapped[str] = mapped_column(
		sqlalchemy.String(32), nullable=True
	)
	phone_number: Mapped[str] = mapped_column(
		sqlalchemy.String(20), nullable=True
	)
	s3_avatar_file: Mapped[str] = mapped_column(
		sqlalchemy.String(64), nullable=True
	)
	position_id: Mapped[int] = mapped_column(
		sqlalchemy.ForeignKey(
			'land_bank_position.id', ondelete='RESTRICT'
		), nullable=True
	)
	department_id: Mapped[UUID] = mapped_column(
		sqlalchemy.ForeignKey(
			'land_bank_department.id', ondelete='RESTRICT'
		), nullable=True
	)
	employee_head_id: Mapped[UUID] = mapped_column(
		sqlalchemy.ForeignKey(
			'land_bank_employee.id', ondelete='RESTRICT'
		), nullable=True
	)

	employee_head: Mapped['Employee'] = relationship(
		'Employee', back_populates='subordinates', remote_side='Employee.id'
	)
	subordinates: Mapped[List['Employee']] = relationship(
		'Employee', back_populates='employee_head'
	)

	position: Mapped['Position'] = relationship(
		'Position', back_populates='employees'
	)
	department: Mapped['Department'] = relationship(
		'Department', back_populates='employees'
	)


class Department(Base):
	__tablename__ = 'land_bank_department'

	department_name: Mapped[str] = mapped_column(
		sqlalchemy.String(64), unique=True, nullable=False
	)

	employees: Mapped[List['Employee']] = relationship(
		'Employee', back_populates='department'
	)


class Position(Base):
	__tablename__ = 'land_bank_position'

	position_name: Mapped[str] = mapped_column(
		sqlalchemy.String(64), nullable=False,
		unique=True
	)
	is_director_position: Mapped[bool] = mapped_column(
		sqlalchemy.Boolean, default=False
	)

	employees: Mapped[List['Employee']] = relationship(
		'Employee', back_populates='position'
	)

	permissions: Mapped[List['PermissionPosition']] = relationship(
		'PermissionPosition', back_populates='position'
	)


class PermissionPosition(Base):
	__tablename__ = 'permission_position'

	position_id: Mapped[int] = mapped_column(
		sqlalchemy.ForeignKey('land_bank_position.id', ondelete='RESTRICT'),
		nullable=False
	)
	permission_id: Mapped[int] = mapped_column(
		sqlalchemy.ForeignKey('permissions.id', ondelete='CASCADE'),
		nullable=False
	)
	position: Mapped['Position'] = relationship(
		'Position', back_populates='permissions'
	)
	permission: Mapped['Permission'] = relationship(
		'Permission', back_populates='positions'
	)


class Permission(Base):
	__tablename__ = 'permissions'

	permission_name: Mapped[str] = mapped_column(
		sqlalchemy.String(length=64),
		unique=True
	)
	positions: Mapped[List['PermissionPosition']] = relationship(
		'PermissionPosition', back_populates='permission'
	)


class AreaComment(Base):
	__tablename__ = 'area_comments'

	comment_text: Mapped[str] = mapped_column(
		sqlalchemy.String(128), nullable=False,
	)
	land_area_id: Mapped[UUID] = mapped_column(
		sqlalchemy.ForeignKey('cadastral_land_area.id', ondelete='CASCADE'),
	)
	employee_id: Mapped[UUID] = mapped_column(
		sqlalchemy.ForeignKey('land_bank_employee.id', ondelete='CASCADE')
	)
	created_at: Mapped[datetime] = mapped_column(
		sqlalchemy.DateTime, default=datetime.now
	)

	employee: Mapped['Employee'] = relationship(
		'Employee', backref='land_area_comments'
	)
	land_area: Mapped['LandArea'] = relationship(
		'LandArea', back_populates='comments'
	)


class LandArea(Base):
	__tablename__ = 'cadastral_land_area'

	name: Mapped[str] = mapped_column(
		sqlalchemy.String(length=64), nullable=False
	)
	cadastral_number: Mapped[str] = mapped_column(
		sqlalchemy.String(length=32), nullable=False,
	)
	area_category: Mapped[str] = mapped_column(
		sqlalchemy.String(length=64), nullable=False,
	)
	area_square: Mapped[float] = mapped_column(
		sqlalchemy.Double, nullable=False,
	)
	address: Mapped[str] = mapped_column(
		sqlalchemy.String(length=64), nullable=False
	)
	search_channel: Mapped[str] = mapped_column(
		sqlalchemy.String(length=32), nullable=False
	)
	entered_at_base: Mapped[datetime] = mapped_column(
		sqlalchemy.DateTime, default=datetime.now
	)
	working_status_id: Mapped[UUID] = mapped_column(
		sqlalchemy.ForeignKey('area_working_statuses.id', ondelete='RESTRICT'),
		nullable=False,
	)
	stage_id: Mapped[UUID] = mapped_column(
		sqlalchemy.ForeignKey('area_stages.id', ondelete='RESTRICT'),
		nullable=False
	)

	archive_info: Mapped[Optional['ArchiveInfo']] = relationship(
		'ArchiveInfo', back_populates='land_area'
	)

	stage: Mapped['Stage'] = relationship(
		'Stage', back_populates='land_areas'
	)

	status: Mapped['Status'] = relationship(
		'Status', back_populates='land_areas'
	)

	area_buildings: Mapped[List['Building']] = relationship(
		'Building', back_populates='land_area'
	)

	owners: Mapped[List['LandOwner']] = relationship(
		'LandOwner', back_populates='land_area'
	)

	comments: Mapped[List['AreaComment']] = relationship(
		'AreaComment', back_populates='land_area'
	)

	tasks: Mapped[List['LandAreaTask']] = relationship(
		'LandAreaTask', back_populates='land_area'
	)


class Building(Base):
	__tablename__ = 'land_area_buildings'

	name: Mapped[Optional[str]] = mapped_column(
		sqlalchemy.String(length=64), nullable=False,
	)
	description: Mapped[Optional[str]] = mapped_column(
		sqlalchemy.String(length=128), nullable=True
	)
	commissioning_year: Mapped[str] = mapped_column(
		sqlalchemy.String(length=4), nullable=False
	)
	land_area_id: Mapped[UUID] = mapped_column(
		sqlalchemy.ForeignKey('cadastral_land_area.id', ondelete='CASCADE'),
		nullable=False
	)

	land_area: Mapped['LandArea'] = relationship(
		'LandArea', back_populates='area_buildings'
	)


class LandOwner(Base):
	__tablename__ = 'land_area_objects_owners'

	name: Mapped[str] = mapped_column(
		sqlalchemy.String(length=64), nullable=False,
	)
	email: Mapped[str] = mapped_column(
		sqlalchemy.String(length=64), nullable=True,
	)
	phone_number: Mapped[str] = mapped_column(
		sqlalchemy.String(length=16), nullable=False,
	)
	location: Mapped[str] = mapped_column(
		sqlalchemy.String(length=128), nullable=True,
	)
	land_area_id: Mapped[UUID] = mapped_column(
		sqlalchemy.ForeignKey('cadastral_land_area.id', ondelete='CASCADE'),
	)

	land_area: Mapped['LandArea'] = relationship(
		'LandArea', back_populates='owners'
	)


class ArchiveInfo(Base):
	__tablename__ = 'area_archived_infos'

	archived_at: Mapped[datetime] = mapped_column(
		sqlalchemy.DateTime, default=datetime.now
	)
	comment: Mapped[str] = mapped_column(
		sqlalchemy.String(length=128), nullable=True
	)
	land_area_id: Mapped[UUID] = mapped_column(
		sqlalchemy.ForeignKey('cadastral_land_area.id', ondelete='CASCADE'),
		nullable=False
	)

	land_area: Mapped['LandArea'] = relationship(
		'LandArea', back_populates='archive_info'
	)


class Stage(Base):
	__tablename__ = 'area_stages'

	stage_name: Mapped[str] = mapped_column(
		sqlalchemy.String(length=32), nullable=False, unique=True
	)

	land_areas: Mapped[List['LandArea']] = relationship(
		'LandArea', back_populates='stage'
	)


class Status(Base):
	__tablename__ = 'area_working_statuses'

	status_name: Mapped[str] = mapped_column(
		sqlalchemy.String(length=32), nullable=False, unique=True
	)

	land_areas: Mapped[List['LandArea']] = relationship(
		'LandArea', back_populates='status'
	)


class LandAreaTask(Base):
	__tablename__ = 'land_area_tasks'

	name: Mapped[str] = mapped_column(
		sqlalchemy.String(length=64),
		nullable=False
	)
	description: Mapped[str] = mapped_column(
		sqlalchemy.String(length=128),
		nullable=True
	)
	executor_id: Mapped[UUID] = mapped_column(
		sqlalchemy.ForeignKey(
			'land_bank_employee.id', ondelete='RESTRICT'
		), nullable=False
	)
	author_id: Mapped[UUID] = mapped_column(
		sqlalchemy.ForeignKey(
			'land_bank_employee.id', ondelete='RESTRICT'
		), nullable=False
	)
	land_area_id: Mapped[UUID] = mapped_column(
		sqlalchemy.ForeignKey(
			'cadastral_land_area.id', ondelete='CASCADE'
		), nullable=False
	)
	status: Mapped[str] = mapped_column(
		sqlalchemy.String(length=32), nullable=False
	)
	started_at: Mapped[datetime] = mapped_column(
		sqlalchemy.DateTime, default=datetime.utcnow
	)
	deadline: Mapped[datetime] = mapped_column(
		sqlalchemy.DateTime, nullable=False
	)

	executor: Mapped[Employee] = relationship(
		'Employee', backref='tasks', foreign_keys=[executor_id]
	)
	author: Mapped[Employee] = relationship(
		'Employee', backref='created_tasks', foreign_keys=[author_id]
	)
	land_area: Mapped[LandArea] = relationship(
		'LandArea', back_populates='tasks'
	)
