from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import ScalarResult, delete, insert, select

from domain.juristic_data.schemas import LimitSchema
from infrastructure.database.model import LandAreaLimit, Limit


class LimitRepository:
	def __init__(self):
		self.__model = Limit

	async def create_limit(self, session: AsyncSession, **values) -> Limit:
		statement = insert(Limit).values(**values).returning(Limit)
		return await session.scalar(statement)

	async def select_all(
			self,
			session: AsyncSession
	) -> ScalarResult[Limit]:
		return await session.scalars(select(self.__model))

	async def delete_from_association(
			self,
			session: AsyncSession,
			*filters
	) -> None:
		statement = (
			delete(LandAreaLimit)
			.where(*filters)
		)
		await session.execute(statement)

	async def create_associations(
			self,
			session: AsyncSession,
			land_area_id: UUID,
			schemas: List[LimitSchema]
	) -> ScalarResult[LandAreaLimit]:
		statement = (
			insert(LandAreaLimit)
			.values([
				{
					'limit_id': limit.id,
					'land_area_id': land_area_id
				}
				for limit in schemas
			])
			.returning(LandAreaLimit)
		)
		return await session.scalars(statement)
