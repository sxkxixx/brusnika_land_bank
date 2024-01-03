from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.model import ExtraAreaData
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository

__all__ = ['ExtraDataRepository']


class ExtraDataRepository(SQLAlchemyRepository):
	def __init__(self):
		super().__init__(ExtraAreaData)

	async def create_data(
			self,
			session: AsyncSession,
			**values_set
	) -> ExtraAreaData:
		return await self.create_record(session, **values_set)

	async def update_data(
			self,
			session: AsyncSession,
			*filters,
			**values_set
	) -> ExtraAreaData:
		return await self.update_record(session, *filters, **values_set)

	async def delete_data(
			self,
			session: AsyncSession,
			instance: ExtraAreaData
	) -> None:
		await self.delete_record(session, instance)

	async def get_data(self, session, *filters) -> Optional[ExtraAreaData]:
		return await self.get_record(session, *filters)
