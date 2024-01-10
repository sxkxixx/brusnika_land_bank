from datetime import datetime
from typing import List, Optional, TypeVar
from uuid import UUID, uuid4

import sqlalchemy
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
        sqlalchemy.String(32), nullable=True
    )
    first_name: Mapped[str] = mapped_column(
        sqlalchemy.String(32), nullable=True
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
    position_id: Mapped[UUID] = mapped_column(
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
    cadastral_cost: Mapped[float] = mapped_column(
        sqlalchemy.Double(), nullable=True
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
    working_status: Mapped[str] = mapped_column(
        sqlalchemy.String(length=32), nullable=False,
    )
    stage: Mapped[str] = mapped_column(
        sqlalchemy.String(length=32), nullable=False
    )

    archive_info: Mapped[Optional['ArchiveInfo']] = relationship(
        'ArchiveInfo', back_populates='land_area'
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

    extra_data: Mapped['ExtraAreaData'] = relationship(
        'ExtraAreaData', back_populates='land_area'
    )

    limits: Mapped[List['Limit']] = relationship(
        secondary='land_area__limit', back_populates='land_area_list'
    )
    permitted_uses: Mapped[List['PermittedUse']] = relationship(
        secondary='land_area__permitted_uses', back_populates='land_areas'
    )


class Building(Base):
    __tablename__ = 'land_area_buildings'

    name: Mapped[Optional[str]] = mapped_column(
        sqlalchemy.String(length=64), nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        sqlalchemy.String(length=128), nullable=True
    )
    commissioning_year: Mapped[int] = mapped_column(
        sqlalchemy.Integer, nullable=True
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


# Дополнительная информация и юридические сведения по Земельным участкам
# Связь m2m

class Limit(Base):
    """Ограничения и обременения"""

    __tablename__ = 'area_limits'

    name: Mapped[str] = mapped_column(
        sqlalchemy.String(length=64), nullable=False, unique=True
    )

    land_area_list: Mapped[List['LandArea']] = relationship(
        secondary='land_area__limit', back_populates='limits'
    )


class LandAreaLimit(Base):
    """Ассоциативная таблица для таблиц cadastral_land_area и area_limits"""

    __tablename__ = 'land_area__limit'

    limit_id: Mapped[UUID] = mapped_column(
        sqlalchemy.ForeignKey('area_limits.id', ondelete='CASCADE'),
        primary_key=True
    )
    land_area_id: Mapped[UUID] = mapped_column(
        sqlalchemy.ForeignKey('cadastral_land_area.id', ondelete='CASCADE'),
        primary_key=True
    )


class LandAreaPermittedUse(Base):
    """Ассоциативная таблица для таблиц permitted_uses и cadastral_land_area"""

    __tablename__ = 'land_area__permitted_uses'

    permitted_use_id: Mapped[UUID] = mapped_column(
        sqlalchemy.ForeignKey('permitted_uses.id', ondelete='CASCADE'),
        primary_key=True
    )
    land_area_id: Mapped[UUID] = mapped_column(
        sqlalchemy.ForeignKey('cadastral_land_area.id', ondelete='CASCADE'),
        primary_key=True,
    )


class PermittedUse(Base):
    """Виды разрешенного пользования"""
    __tablename__ = 'permitted_uses'

    name: Mapped[str] = mapped_column(
        sqlalchemy.String(length=64), nullable=False,
        unique=True
    )

    land_areas: Mapped[List['LandArea']] = relationship(
        secondary='land_area__permitted_uses',
        back_populates='permitted_uses'
    )


# Дополнительная информация Земельного банка

class ExtraAreaData(Base):
    __tablename__ = 'extra_land_area_data'

    land_area_id: Mapped[UUID] = mapped_column(
        sqlalchemy.ForeignKey('cadastral_land_area.id', ondelete='CASCADE'),
        nullable=False
    )
    engineering_networks: Mapped[str] = mapped_column(
        sqlalchemy.String(length=128), nullable=True
    )
    transport: Mapped[str] = mapped_column(
        sqlalchemy.String(length=128), nullable=True
    )
    result: Mapped[str] = mapped_column(
        sqlalchemy.String(length=256), nullable=True
    )

    land_area: Mapped['LandArea'] = relationship(
        'LandArea', back_populates='extra_data'
    )
