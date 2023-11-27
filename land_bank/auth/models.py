import uuid
from typing import List
from uuid import UUID
import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auth.schemas import EmployeeReadSchema
from core import Base


class Employee(Base):
    """
    Модель данных: "Сотрудник Земельного Банка"
    """
    __tablename__ = 'land_bank_employee'

    id: Mapped[UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
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
        'Employee', back_populates='subordinates'
    )
    subordinates: Mapped[List['Employee']] = relationship(
        'Employee', back_populates='employee_head'
    )

    position: Mapped['Position'] = relationship(
        'Position', back_populates='employees'
    )
    department: Mapped['Department'] = relationship(
        'Department', back_populates='employee'
    )

    @property
    def to_schema(self) -> EmployeeReadSchema:
        return EmployeeReadSchema.from_model(self)


class Department(Base):
    __tablename__ = 'land_bank_department'

    id: Mapped[UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    department_name: Mapped[str] = mapped_column(
        sqlalchemy.String(64), unique=True, nullable=False
    )

    employees: Mapped[List['Employee']] = relationship(
        'Employee', back_populates='department'
    )


class Position(Base):
    __tablename__ = 'land_bank_position'

    id: Mapped[int] = mapped_column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True
    )
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
