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
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repository = SQLAlchemyRepository(self.session, LandAreaTask)

	async def create_task(self, **kwargs) -> LandAreaTask:
		try:
			task: LandAreaTask = await self.repository.create_record(**kwargs)
			await self.session.commit()
			return await self.__get_related(task.id)
		except Exception as e:
			await self.session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()

	async def __get_related(self, id: UUID) -> LandAreaTask:
		return await self.repository.get_record_with_relationships(
			filters=[LandAreaTask.id == id],
			options=[
				selectinload(LandAreaTask.author),
				selectinload(LandAreaTask.executor),
				selectinload(LandAreaTask.land_area)
			]
		)

	async def get_employee_tasks(self, employee_id):
		return await self.repository.select_records(
			filters=[LandAreaTask.executor_id == employee_id],
			options=[
				selectinload(LandAreaTask.land_area)
			]
		)

	async def update_task(self, task_id: UUID, **values_set) -> LandAreaTask:
		try:
			land_area: LandAreaTask = await self.repository.update_record(
				LandAreaTask.id == task_id, **values_set
			)
			await self.session.commit()
			return land_area
		except Exception as e:
			await self.session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()
