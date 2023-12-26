from typing import Optional

from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.exception import rpc_exceptions
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository
from infrastructure.database.model import ExtraAreaData

__all__ = [
	'ExtraDataService'
]


class ExtraDataService:
	def __init__(self):
		self.repository: Optional[SQLAlchemyRepository] = None
		self.session: Optional[AsyncSession] = None

	def set_async_session(self, session: AsyncSession):
		self.session = session
		self.repository = SQLAlchemyRepository(session, ExtraAreaData)

	async def create(self, **kwargs) -> ExtraAreaData:
		try:
			data: ExtraAreaData = await self.repository.create_record(**kwargs)
			await self.session.commit()
			return data
		except IntegrityError | PendingRollbackError as e:
			await self.session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()

	async def update(self, extra_data_id, **values_set) -> ExtraAreaData:
		try:
			data: ExtraAreaData = await self.repository.update_record(
				ExtraAreaData.id == extra_data_id,
				**values_set
			)
			await self.session.commit()
			return data
		except IntegrityError | PendingRollbackError as e:
			await self.session.rollback()
		finally:
			await self.session.close()

