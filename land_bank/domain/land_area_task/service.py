from typing import Iterable, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from infrastructure.database.model import LandAreaTask
from infrastructure.exception import rpc_exceptions
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository

__all__ = [
	'LandAreaTaskService'
]


class LandAreaTaskService:
	def __init__(self):
		self.session: Union[AsyncSession, None] = None
		self.repository: Union[SQLAlchemyRepository, None] = None

	def set_async_session(self, session: AsyncSession):
		self.session: AsyncSession = session
		self.repository: SQLAlchemyRepository = SQLAlchemyRepository(
			self.session, LandAreaTask
		)

	async def create_task(self, **kwargs) -> LandAreaTask:
		try:
			task: LandAreaTask = await self.repository.create_record(**kwargs)
			await self.session.commit()
			return await self.get_task_by_id(task.id)
		except Exception as e:
			await self.session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()

	async def get_employee_tasks(self, executor_id: UUID) -> Iterable[
		LandAreaTask]:
		return await self.__get_tasks(
			filters=[LandAreaTask.executor_id == executor_id],
			options=[selectinload(LandAreaTask.land_area)]
		)

	async def get_area_tasks(self, land_area_id: UUID) -> Iterable[
		LandAreaTask]:
		return await self.__get_tasks(
			filters=[LandAreaTask.land_area_id == land_area_id],
			options=[selectinload(LandAreaTask.executor)]
		)

	async def __get_tasks(self, filters, options) -> Iterable[LandAreaTask]:
		return await self.repository.select_records(
			filters=filters, options=options)

	async def update_task(self, task_id: UUID, **values_set) -> LandAreaTask:
		try:
			task: LandAreaTask = await self.repository.update_record(
				LandAreaTask.id == task_id, **values_set
			)
			await self.session.commit()
			return task
		except Exception as e:
			await self.session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()

	async def get_task_by_id(self, task_id) -> LandAreaTask:
		return await self.repository.get_record_with_relationships(
			filters=[LandAreaTask.id == task_id],
			options=[
				selectinload(LandAreaTask.author),
				selectinload(LandAreaTask.executor),
				selectinload(LandAreaTask.land_area)
			]
		)
