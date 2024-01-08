from sqlalchemy import select
from typing import Any, Callable, Iterable, List, Optional
from uuid import UUID

from sqlalchemy import UnaryExpression, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.request_params.schema import LimitOffset, SortParams
from infrastructure.database.model import AreaComment, LandArea, Limit
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository

__all__ = ['LandAreaRepository']


class LandAreaRepository(SQLAlchemyRepository):
	def __init__(self):
		super().__init__(LandArea)

	async def create_land_area(self, session, **values_set) -> LandArea:
		return await self.create_record(session, **values_set)

	async def get_ordered_lands(
			self,
			session: AsyncSession,
			limit_offset: LimitOffset,
			sort_params: Optional[SortParams]
	) -> Iterable[LandArea]:
		orders = self.__get_sort_expressions(sort_params)
		return await self.select_ordered_records(
			session, offset=limit_offset.offset, limit=limit_offset.limit,
			options=[selectinload(LandArea.owners)],
			orders=orders
		)

	@staticmethod
	def __get_sort_expressions(
			sort_params: Optional[SortParams]
	) -> List[UnaryExpression]:
		if not sort_params:
			return []
		sorting_function: Callable = desc if sort_params.order == 'desc' else \
			asc
		return [
			sorting_function(getattr(LandArea, order_field))
			for order_field in sort_params.fields
		]

	async def get_land_area(
			self,
			session: AsyncSession,
			filters,
			options
	) -> Optional[LandArea]:
		return await self.get_record_with_relationships(
			session, filters, options)

	async def get_land_area_relations(
			self,
			session: AsyncSession,
			land_area_id: UUID
	) -> LandArea:
		return await self.get_record_with_relationships(
			session,
			filters=[LandArea.id == land_area_id],
			options=[
				selectinload(LandArea.area_buildings),
				selectinload(LandArea.owners),
				selectinload(LandArea.comments).selectinload(
					AreaComment.employee),
				selectinload(LandArea.extra_data)
			]
		)

	async def update_land_area(
			self,
			session: AsyncSession,
			land_area_id: UUID,
			**values_set
	) -> LandArea | None:
		return await self.update_record(
			session,
			LandArea.id == land_area_id,
			**values_set)

	async def get_area_with_limits_uses(
			self,
			session: AsyncSession,
			land_area_id: UUID
	):
		return await self.get_record_with_relationships(
			session, filters=[LandArea.id == land_area_id],
			options=[
				selectinload(LandArea.limits),
				selectinload(LandArea.permitted_uses)
			]
		)

	async def update_limits(
			self,
			session: AsyncSession,
			land_area: LandArea,
	):
		pass
