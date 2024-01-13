from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from infrastructure.database.model import TaskComment
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository


class TaskCommentRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(TaskComment)

    async def create_comment(
            self,
            session: AsyncSession,
            **values_set
    ) -> TaskComment:
        comment: TaskComment = await self.create_record(session, **values_set)
        return await self.get_comment_with_employee(session, comment.id)

    async def get_task_comment(
            self,
            session: AsyncSession,
            task_comment_id: UUID
    ) -> Optional[TaskComment]:
        return await self.get_record(
            session,
            TaskComment.id == task_comment_id
        )

    async def get_comment_with_employee(
            self,
            session: AsyncSession,
            comment_id: UUID
    ) -> Optional[TaskComment]:
        return await self.get_record_with_relationships(
            session,
            filters=[TaskComment.id == comment_id],
            options=[selectinload(TaskComment.employee)]
        )

    async def delete_task_comment(
            self,
            session: AsyncSession,
            task_comment: TaskComment
    ) -> None:
        await self.delete_record(session, task_comment)
