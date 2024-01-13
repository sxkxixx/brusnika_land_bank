from typing import Iterable, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from infrastructure.database.model import LandAreaTask, TaskComment
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository

__all__ = [
    'LandAreaTaskRepository'
]


class LandAreaTaskRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(LandAreaTask)

    async def create_task(
            self,
            session: AsyncSession,
            **kwargs
    ) -> LandAreaTask:
        land_area_task: LandAreaTask = await self.create_record(
            session, **kwargs
        )
        return await self.get_task_related(session, land_area_task.id)

    async def update_task(
            self,
            session: AsyncSession,
            *filters,
            **values_set
    ) -> LandAreaTask:
        return await self.update_record(session, *filters, **values_set)

    async def get_task(
            self,
            session: AsyncSession,
            *filters
    ) -> Optional[LandAreaTask]:
        return await self.get_record(session, *filters)

    async def get_employee_tasks(
            self,
            session: AsyncSession,
            employee_id: UUID
    ) -> Iterable[LandAreaTask]:
        return await self.select_records(
            session,
            filters=[LandAreaTask.executor_id == employee_id],
            options=[selectinload(LandAreaTask.land_area)]
        )

    async def get_area_tasks(
            self,
            session: AsyncSession,
            land_area_id: UUID
    ) -> Iterable[LandAreaTask]:
        return await self.select_records(
            session,
            filters=[LandAreaTask.land_area_id == land_area_id],
            options=[selectinload(LandAreaTask.executor)]
        )

    async def get_task_related(
            self,
            session: AsyncSession,
            task_id: UUID
    ) -> Optional[LandAreaTask]:
        return await self.get_record_with_relationships(
            session, filters=[LandAreaTask.id == task_id],
            options=[
                selectinload(LandAreaTask.executor),
                selectinload(LandAreaTask.author),
                selectinload(LandAreaTask.land_area),
                selectinload(
                    LandAreaTask.task_comments
                ).selectinload(
                    TaskComment.employee
                )
            ]
        )

    async def is_task_exists(self, session: AsyncSession, *filters) -> bool:
        task: LandAreaTask = await self.get_record(session, *filters)
        if not task:
            return False
        return True
