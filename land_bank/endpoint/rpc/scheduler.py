from typing import Iterable, List, Optional
from uuid import UUID

from fastapi import Depends
from fastapi_jsonrpc import Entrypoint
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dependency import AuthenticationDependency
from domain.scheduler_task.schema import (
    SchedulerTaskResponseDTO,
    TaskListResponseDTO,
    TaskRequestDTO,
    TaskRelatedResponseDTO,
    TaskEditRequestDTO,
    TaskResponseDTO
)
from domain.task_comment.schema import (
    TaskCommentRequestDTO,
    TaskCommentResponseDTO
)
from infrastructure.database.model import Employee, LandAreaTask, TaskComment
from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from infrastructure.database.transaction import in_transaction
from infrastructure.exception import rpc_exceptions
from storage.scheduler_task import LandAreaTaskRepository
from storage.task_comment import TaskCommentRepository

router = Entrypoint(
    path='/api/v1/scheduler',
    tags=['SCHEDULER']
)
task_repository: LandAreaTaskRepository = LandAreaTaskRepository()
task_comment_repository: TaskCommentRepository = TaskCommentRepository()


@router.method(
    errors=[
        rpc_exceptions.AuthenticationError,
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
    return TaskRelatedResponseDTO.model_validate(
        created_task, from_attributes=True
    )


@router.method(
    errors=[
        rpc_exceptions.AuthenticationError,
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
        rpc_exceptions.TransactionError
    ],
    dependencies=[
        Depends(AuthenticationDependency())
    ]
)
@in_transaction
async def delete_land_area_task(
        task_id: UUID
) -> None:
    session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    task: Optional[LandAreaTask] = await task_repository.get_record(
        session, LandAreaTask.id == task_id)
    if not task:
        raise rpc_exceptions.ObjectNotFoundError(
            data='No task by this ID')
    await task_repository.delete_record(session, task)
    return None


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


@router.method(
    errors=[rpc_exceptions.TransactionError]
)
@in_transaction
async def add_task_comment(
        comment: TaskCommentRequestDTO,
        employee: Employee = Depends(AuthenticationDependency()),
) -> TaskCommentResponseDTO:
    session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    if not await task_repository.is_task_exists(
            session, LandAreaTask.id == comment.task_id):
        raise rpc_exceptions.ObjectNotFoundError(data='No task by this id')
    orm_comment: TaskComment = await task_comment_repository.create_comment(
        session, **comment.model_dump(), employee_id=employee.id
    )
    return TaskCommentResponseDTO.model_validate(
        orm_comment, from_attributes=True
    )


@router.method(errors=[rpc_exceptions.TransactionError])
@in_transaction
async def delete_task_comment(
        task_comment_id: UUID,
        employee: Employee = Depends(AuthenticationDependency())
) -> None:
    session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    comment: Optional[
        TaskComment] = await task_comment_repository.get_task_comment(
        session, task_comment_id
    )
    if not comment:
        raise rpc_exceptions.ObjectNotFoundError(data='No comment by this id')
    if comment.employee_id != employee.id:
        raise rpc_exceptions.TransactionForbiddenError(
            data='Forbidden to delete someone else\'s comment')
    await task_comment_repository.delete_task_comment(session, comment)
    return None
