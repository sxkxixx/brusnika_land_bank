from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.land_area.schema import BuildingRequestDTO
from infrastructure.database.model import Building
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository

__all__ = [
	'BuildingRepository'
]


class BuildingRepository(SQLAlchemyRepository):
	def __init__(self):
		super().__init__(Building)

	async def create_building(
			self,
			session: AsyncSession,
			**values_set
	) -> Building:
		return await self.create_record(session, **values_set)

	async def create_buildings(
			self,
			session: AsyncSession,
			land_area_id: UUID,
			building_schema_list: List[BuildingRequestDTO]
	) -> List[Building]:
		buildings = []
		for building in building_schema_list:
			buildings.append(
				await self.create_building(
					session, land_area_id=land_area_id, **building.model_dump())
			)
		return buildings

	async def update_building(
			self,
			session: AsyncSession,
			building_id: UUID,
			**values_set
	) -> Building:
		return await self.update_record(
			session,
			Building.id == building_id,
			**values_set
		)
