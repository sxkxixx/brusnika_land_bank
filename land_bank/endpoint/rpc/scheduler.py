from typing import Iterable, List, Optional
from uuid import UUID

from fastapi import Depends
from fastapi_jsonrpc import Entrypoint
from sqlalchemy.ext.asyncio import AsyncSession

from domain.scheduler_task.schema import (
	SchedulerTaskResponseDTO,
	TaskListResponseDTO,
	TaskRequestDTO,
	TaskRelatedResponseDTO,
	TaskEditRequestDTO,
	TaskResponseDTO
)
from infrastructure.database.model import Employee, LandAreaTask
from infrastructure.database.transaction import in_transaction
from infrastructure.exception import rpc_exceptions
from application.auth.dependency import AuthenticationDependency
from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from storage.scheduler_task import LandAreaTaskRepository

router = Entrypoint(
	path='/api/v1/scheduler',
	tags=['SCHEDULER']
)
task_repository: LandAreaTaskRepository = LandAreaTaskRepository()


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.AuthorizationError,
		rpc_exceptions.TransactionError
	]
)
@in_transaction
async def create_land_area_task(
		task: TaskRequestDTO,
		employee: Employee = Depends(AuthenticationDependency()),
) -> TaskRelatedResponseDTO:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	created_task: LandAreaTask = await task_repository.create_task(
		session, **task.model_dump(), author_id=employee.id
	)
	return TaskRelatedResponseDTO.model_validate(created_task, from_attributes=True)


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
@in_transaction
async def update_land_area_task(
		task_id: UUID,
		edited_task: TaskEditRequestDTO,
) -> TaskResponseDTO:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	if not await task_repository.is_task_exists(
			session, LandAreaTask.id == task_id):
		raise rpc_exceptions.ObjectNotFoundError()
	task: LandAreaTask = await task_repository.update_task(
		session, LandAreaTask.id == task_id, **edited_task.model_dump())
	return TaskResponseDTO.model_validate(task, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
	]
)
@in_transaction
async def get_employee_tasks(
		employee: Employee = Depends(AuthenticationDependency()),
) -> List[SchedulerTaskResponseDTO]:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	tasks: Iterable[LandAreaTask] = await task_repository.get_employee_tasks(
		session, employee.id)
	return [
		SchedulerTaskResponseDTO.model_validate(task, from_attributes=True)
		for task in tasks
	]


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
@in_transaction
async def get_area_tasks(
		land_area_id: UUID,
) -> List[TaskListResponseDTO]:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	tasks: Iterable[LandAreaTask] = await task_repository.get_area_tasks(
		session, land_area_id)
	return [
		TaskListResponseDTO.model_validate(task, from_attributes=True)
		for task in tasks
	]


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.ObjectNotFoundError
	],
	dependencies=[Depends(AuthenticationDependency())]
)
@in_transaction
async def get_task_by_id(
		task_id: UUID,
) -> TaskRelatedResponseDTO:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	task: Optional[LandAreaTask] = await task_repository.get_task_related(
		session, task_id)
	if not task:
		raise rpc_exceptions.ObjectNotFoundError(data='No task by this id')
	return TaskRelatedResponseDTO.model_validate(task, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.ObjectNotFoundError
	],
	dependencies=[Depends(AuthenticationDependency())]
)
@in_transaction
async def change_task_status(
		task_id: UUID,
		status_name: str,
) -> TaskResponseDTO:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	if not await task_repository.is_task_exists(
			session, LandAreaTask.id == task_id):
		raise rpc_exceptions.ObjectNotFoundError()
	task: LandAreaTask = await task_repository.update_task(
		session, LandAreaTask.id == task_id, status=status_name)
	return TaskResponseDTO.model_validate(task, from_attributes=True)
