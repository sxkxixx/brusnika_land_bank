from typing import List
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core import rpc_exceptions
from bank.models import LandArea
from layers.repositories import (
	SQLAlchemyRepositoryV1,
	LandAreaRepository,
	BuildingRepository,
	LandOwnerRepository,
	StageRepository, StatusRepository
)


class LandAreaService:
	def __init__(
			self,
			session: AsyncSession
	):
		self.session = session
		self.__land_area_repository = LandAreaRepository(self.session)
		self.__area_building_repository = BuildingRepository(
			self.session)
		self.__area_owner_repository = LandOwnerRepository(self.session)

	async def get_ordered_lands(
			self,
			limit_offset,
			sort_params,
	):
		...

	async def __create_land_area_related_objects(
			self,
			land_area_id: UUID,
			repository: SQLAlchemyRepositoryV1,
			schemas: List[BaseModel]
	):
		"""
		Создает зависимые записи для земельного участка
		:param land_area_id: ID земельного участка
		:param repository: Репозиторий
		:param schemas: Список схем
		:return:
		"""
		for schema in schemas:
			await repository.create_record(
				**schema.model_dump(),
				land_area_id=land_area_id
			)

	async def create_land_area(
			self,
			schema_land_area: BaseModel,
			schemas_area_owners: List[BaseModel],
			schemas_buildings: List[BaseModel]
	):
		"""
		Транзакция для создания земельного участка, строений и владельцев ЗУ.
		:param schema_land_area:  Схема земельного участка
		:param schemas_area_owners: Список схем собственников
		:param schemas_buildings: Список схем обхектов
		:return: Возвращает земельный участок с отношениями.
		"""
		status = await StatusRepository(self.session).get_or_create_record(
			status_name='WAITING_TO_DECISION')
		stage = await StageRepository(self.session).get_or_create_record(
			stage_name='SEARCH')
		land_area: LandArea = await self.__land_area_repository.create_record(
			**schema_land_area.model_dump(), working_status_id=status.id,
			stage_id=stage.id)
		await self.__create_land_area_related_objects(
			land_area.id, self.__area_owner_repository, schemas_area_owners)
		await self.__create_land_area_related_objects(
			land_area.id, self.__area_building_repository, schemas_buildings)
		try:
			await self.session.commit()
			return await self.get_land_area(
				filters=[LandArea.id == land_area.id],
				options=[
					selectinload(LandArea.area_buildings),
					selectinload(LandArea.status),
					selectinload(LandArea.stage),
					selectinload(LandArea.owners)
				]
			)
		except Exception as e:
			await self.session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()

	async def get_land_area(self, filters, options) -> LandArea:
		"""
		Возвращает Земельный Участок с отношениями (статус, этап, постройки,
		собственники)
		:param filters: Параметры фильтрации
		:param options: Отношения для подгрузки
		:return: Земельный участок
		"""
		return await self.__land_area_repository.get_record_with_relationships(
			filters=filters, options=options
		)
