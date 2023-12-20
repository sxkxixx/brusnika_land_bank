from typing import Iterable, List
from uuid import UUID

from fastapi import Depends
from fastapi_jsonrpc import Entrypoint
from sqlalchemy.ext.asyncio import AsyncSession

from domain.land_area_task.schema import (
	TaskRequestDTO,
	TaskRelatedResponseDTO,
	ListTaskResponseDTO,
	EditTaskRequestDTO
)
from domain.land_area_task.service import LandAreaTaskService
from infrastructure.database.model import Employee, LandAreaTask
from infrastructure.exception import rpc_exceptions
from application.auth.dependency import AuthorizationDependency, \
	AuthenticationDependency
from infrastructure.database.session import async_session_generator

router = Entrypoint('/api/v1/scheduler', tags=['SCHEDULER'])


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.AuthorizationError,
		rpc_exceptions.TransactionError
	]
)
async def create_land_area_task(
		task: TaskRequestDTO,
		employee: Employee = Depends(AuthorizationDependency(
			permission_name='Can create land area task')),
		session: AsyncSession = Depends(async_session_generator)
) -> TaskRelatedResponseDTO:
	service = LandAreaTaskService(session)
	task: LandAreaTask = await service.create_task(
		**task.model_dump(), author_id=employee.id, status='CREATED'
	)
	return TaskRelatedResponseDTO.model_validate(task, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.AuthorizationError,
		rpc_exceptions.TransactionError
	],
	dependencies=[
		Depends(AuthorizationDependency(
				permission_name='Can edit land area task'))
	]
)
async def update_land_area_task(
		id: UUID,
		task: EditTaskRequestDTO,
		session: AsyncSession = Depends(async_session_generator)
):
	service: LandAreaTaskService = LandAreaTaskService(session)
	land_area_task: LandAreaTask = await service.update_task(
		task_id=id, **task.model_dump())
	return land_area_task


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.AuthorizationError,
	]
)
async def get_employee_tasks(
		employee: Employee = Depends(AuthenticationDependency()),
		session: AsyncSession = Depends(async_session_generator)
) -> List[ListTaskResponseDTO]:
	service: LandAreaTaskService = LandAreaTaskService(session)
	tasks: Iterable[LandAreaTask] = await service.get_employee_tasks(
		employee.id)
	return [
		ListTaskResponseDTO.model_validate(task, from_attributes=True)
		for task in tasks
	]
