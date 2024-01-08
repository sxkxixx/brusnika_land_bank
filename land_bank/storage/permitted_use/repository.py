from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import ScalarResult, delete, insert, select

from domain.juristic_data.schemas import PermittedUseSchema
from infrastructure.database.model import PermittedUse, LandAreaPermittedUse


class PermittedUseRepository:
	def __init__(self):
		self.__model = PermittedUse

	async def select_all(
			self,
			session: AsyncSession
	) -> ScalarResult[PermittedUse]:
		return await session.scalars(select(self.__model))

	async def delete_from_association(
			self,
			session: AsyncSession,
			*filters
	) -> None:
		statement = (
			delete(LandAreaPermittedUse)
			.where(*filters)
		)
		await session.execute(statement)

	async def create_associations(
			self,
			session: AsyncSession,
			land_area_id: UUID,
			schemas: List[PermittedUseSchema]
	) -> ScalarResult[LandAreaPermittedUse]:
		statement = (
			insert(LandAreaPermittedUse)
			.values([
				{
					'permitted_use_id': schema.id,
					'land_area_id': land_area_id
				}
				for schema in schemas
			])
			.returning(LandAreaPermittedUse)
		)
		return await session.scalars(statement)
