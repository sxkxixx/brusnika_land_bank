from typing import Iterable, List
from uuid import UUID

from fastapi import Depends
from fastapi_jsonrpc import Entrypoint
from sqlalchemy.ext.asyncio import AsyncSession

from domain.land_area_task.schema import (
	SchedulerTaskResponseDTO,
	TaskListResponseDTO,
	TaskRequestDTO,
	TaskRelatedResponseDTO,
	TaskEditRequestDTO,
	TaskResponseDTO
)
from domain.land_area_task.service import LandAreaTaskService
from infrastructure.database.model import Employee, LandAreaTask
from infrastructure.exception import rpc_exceptions
from application.auth.dependency import AuthenticationDependency
from infrastructure.database.session import async_session_generator

router = Entrypoint('/api/v1/scheduler', tags=['SCHEDULER'])
task_service: LandAreaTaskService = LandAreaTaskService()


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.AuthorizationError,
		rpc_exceptions.TransactionError
	]
)
async def create_land_area_task(
		task: TaskRequestDTO,
		employee: Employee = Depends(AuthenticationDependency()),
		session: AsyncSession = Depends(async_session_generator)
) -> TaskRelatedResponseDTO:
	task_service.set_async_session(session)
	task: LandAreaTask = await task_service.create_task(
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
		Depends(AuthenticationDependency())
	]
)
async def update_land_area_task(
		task_id: UUID,
		task: TaskEditRequestDTO,
		session: AsyncSession = Depends(async_session_generator)
) -> TaskResponseDTO:
	task_service.set_async_session(session)
	task: LandAreaTask = await task_service.update_task(
		task_id=task_id, **task.model_dump())
	return TaskResponseDTO.model_validate(task, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
	]
)
async def get_employee_tasks(
		employee: Employee = Depends(AuthenticationDependency()),
		session: AsyncSession = Depends(async_session_generator)
) -> List[SchedulerTaskResponseDTO]:
	task_service.set_async_session(session)
	tasks: Iterable[LandAreaTask] = await task_service.get_employee_tasks(
		employee.id)
	return [
		SchedulerTaskResponseDTO.model_validate(task, from_attributes=True)
		for task in tasks
	]


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError
	],
	dependencies=[
		Depends(AuthenticationDependency())
	]
)
async def get_area_tasks(
		land_area_id: UUID,
		session: AsyncSession = Depends(async_session_generator)
) -> List[TaskListResponseDTO]:
	task_service.set_async_session(session)
	tasks = await task_service.get_area_tasks(land_area_id)
	return [
		TaskListResponseDTO.model_validate(task, from_attributes=True)
		for task in tasks
	]


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.ObjectDoesNotExistsError
	],
	dependencies=[Depends(AuthenticationDependency())]
)
async def get_task_by_id(
		task_id: UUID,
		session: AsyncSession = Depends(async_session_generator)
) -> TaskRelatedResponseDTO:
	task_service.set_async_session(session)
	task: LandAreaTask = await task_service.get_task_by_id(task_id)
	if not task:
		raise rpc_exceptions.ObjectDoesNotExistsError(
			data='No task by this id')
	return TaskRelatedResponseDTO.model_validate(task, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.ObjectDoesNotExistsError
	],
	dependencies=[Depends(AuthenticationDependency())]
)
async def change_task_status(
		task_id: UUID,
		status_name: str,
		session: AsyncSession = Depends(async_session_generator)
) -> TaskResponseDTO:
	task_service.set_async_session(session)
	task: LandAreaTask = await task_service.update_task(
		task_id, status=status_name)
	return TaskResponseDTO.model_validate(task, from_attributes=True)
