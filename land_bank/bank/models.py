import uuid
from datetime import datetime
from typing import List, Optional
import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auth.models import Employee
from core import Base

__all__ = [
    'AreaComment',
    'LandArea',
    'Building',
    'LandOwner',
    'ArchiveInfo',
    'Stage',
    'Status',
]


class AreaComment(Base):
    __tablename__ = 'area_comments'

    id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True), primary_key=True,
        default=uuid.uuid4
    )
    comment_text: Mapped[str] = mapped_column(
        sqlalchemy.String(128), nullable=False,
    )
    land_area_id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.ForeignKey('cadastral_land_area.id', ondelete='CASCADE'),
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
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

    id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
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
    working_status_id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.ForeignKey('area_working_statuses.id', ondelete='RESTRICT'),
        nullable=False,
    )
    stage_id: Mapped[uuid.UUID] = mapped_column(
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


class Building(Base):
    __tablename__ = 'land_area_buildings'

    id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True), primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[Optional[str]] = mapped_column(
        sqlalchemy.String(length=64), nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        sqlalchemy.String(length=128), nullable=True
    )
    commissioning_year: Mapped[str] = mapped_column(
        sqlalchemy.String(length=4), nullable=False
    )
    land_area_id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.ForeignKey('cadastral_land_area.id', ondelete='CASCADE'),
        nullable=False
    )

    land_area: Mapped['LandArea'] = relationship(
        'LandArea', back_populates='area_buildings'
    )


class LandOwner(Base):
    __tablename__ = 'land_area_objects_owners'

    id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True), primary_key=True,
        default=uuid.uuid4
    )
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
    land_area_id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.ForeignKey('cadastral_land_area.id', ondelete='CASCADE'),
    )

    land_area: Mapped['LandArea'] = relationship(
        'LandArea', back_populates='owners'
    )


class ArchiveInfo(Base):
    __tablename__ = 'area_archived_infos'

    id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True), primary_key=True,
        default=uuid.uuid4
    )
    archived_at: Mapped[datetime] = mapped_column(
        sqlalchemy.DateTime, default=datetime.now
    )
    comment: Mapped[str] = mapped_column(
        sqlalchemy.String(length=128), nullable=True
    )
    land_area_id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.ForeignKey('cadastral_land_area.id', ondelete='CASCADE'),
        nullable=False
    )

    land_area: Mapped['LandArea'] = relationship(
        'LandArea', back_populates='archive_info'
    )


class Stage(Base):
    __tablename__ = 'area_stages'

    id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True), primary_key=True,
        default=uuid.uuid4
    )
    stage_name: Mapped[str] = mapped_column(
        sqlalchemy.String(length=32), nullable=False, unique=True
    )

    land_areas: Mapped[List['LandArea']] = relationship(
        'LandArea', back_populates='stage'
    )


class Status(Base):
    __tablename__ = 'area_working_statuses'

    id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True), primary_key=True,
        default=uuid.uuid4
    )
    status_name: Mapped[str] = mapped_column(
        sqlalchemy.String(length=32), nullable=False, unique=True
    )

    land_areas: Mapped[List['LandArea']] = relationship(
        'LandArea', back_populates='status'
    )
