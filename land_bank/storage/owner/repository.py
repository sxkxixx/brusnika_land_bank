from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.land_area.schema import OwnerRequestDTO
from infrastructure.database.model import LandOwner
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository

__all__ = ['OwnerRepository']


class OwnerRepository(SQLAlchemyRepository):
	def __init__(self):
		super().__init__(LandOwner)

	async def create_owner(
			self,
			session: AsyncSession,
			**values_set
	) -> LandOwner:
		return await self.create_record(session, **values_set)

	async def create_owners(
			self,
			session: AsyncSession,
			land_area_id: UUID,
			owners_schemas: List[OwnerRequestDTO],
	) -> List[LandOwner]:
		owners = []
		for owner in owners_schemas:
			owners.append(
				await self.create_owner(
					session, **owner.model_dump(), land_area_id=land_area_id
				)
			)
		return owners

	async def update_owner(
			self,
			session: AsyncSession,
			owner_id: UUID,
			**values_set
	) -> LandOwner:
		return await self.update_record(
			session,
			LandOwner.id == owner_id,
			**values_set
		)
