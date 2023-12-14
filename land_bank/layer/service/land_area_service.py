from dataclasses import dataclass
from typing import Callable, Iterable, List
from uuid import UUID
from enum import Enum

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import desc, asc
from core import rpc_exceptions
from bank.model import LandArea, Stage, Status
from layer.repository import (
	SQLAlchemyRepositoryV1,
	LandAreaRepository,
	BuildingRepository,
	LandOwnerRepository,
	StageRepository, StatusRepository
)


@dataclass
class StatusData:
	NEW: str = 'Новый'
	IN_PROGRESS: str = 'В работе'
	WAITING_TO_DECISION: str = 'Ждёт решения'


_next_status = {
	StatusData.NEW: StatusData.IN_PROGRESS,
	StatusData.IN_PROGRESS: StatusData.WAITING_TO_DECISION
}


@dataclass
class StageData:
	SEARCH: str = 'Поиск'
	ANALYZE: str = 'Анализ'
	DEAL: str = 'Сделка'


_next_stage = {
	StageData.SEARCH: StageData.ANALYZE,
	StageData.ANALYZE: StageData.DEAL
}


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
	) -> Iterable['LandArea']:
		options = [selectinload(LandArea.status), selectinload(LandArea.stage)]
		sorting_function: Callable = desc if sort_params.order == 'desc' else \
			asc
		orders = [
			sorting_function(getattr(LandArea, order_field)) for order_field in
			sort_params.fields
		]
		land_areas_list = await (
			self.__land_area_repository.select_ordered_records(
				offset=limit_offset.offset,
				limit=limit_offset.limit,
				options=options,
				orders=orders
			))
		return land_areas_list

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
			status_name=StatusData.NEW)
		stage = await StageRepository(self.session).get_or_create_record(
			stage_name=StageData.SEARCH)
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

	async def update_land_area_service(self, id: UUID, **values_set):
		"""
		Метод сервиса для обновления земельного участка
		:param id: Идентификатор земельного участка
		:param values_set: Значения для обновления
		:return: Обновленный ЗУ
		"""
		land_area: LandArea = await (
			self.__land_area_repository.get_record_with_relationships(
				filters=[LandArea.id == id],
				options=[selectinload(LandArea.status)]
			))
		if not land_area:
			raise rpc_exceptions.ObjectDoesNotExistsError(
				data='No such land area by this id')
		if land_area.status.status_name != StatusData.NEW:
			raise rpc_exceptions.TransactionForbiddenError(
				data='Land area status has changed')
		try:
			land_area = await self.__land_area_repository.update_record(
				LandArea.id == id,
				**values_set
			)
			await self.session.commit()
			return land_area
		except Exception as e:
			await self.session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()

	async def change_status(self, id: UUID) -> Status:
		land_area: LandArea = (
			self.__land_area_repository.get_record_with_relationships(
				filters=[LandArea.id == id],
				options=[selectinload(LandArea.status)]
			))
		status = await StatusRepository(self.session).get_or_create_record(
			status_name=_next_status.get(land_area.status.status_name))
		try:
			await self.__land_area_repository.update_record(
				LandArea.id == land_area.id, status_id=status.id
			)
			await self.session.commit()
			return status
		except Exception as e:
			await self.session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()

	async def change_stage(self, id) -> Stage:
		land_area: LandArea = (
			self.__land_area_repository.get_record_with_relationships(
				filters=[LandArea.id == id],
				options=[selectinload(LandArea.status)]
			))
		stage: Stage = await StageRepository(self.session).get_or_create_record(
			stage_name=_next_stage.get(land_area.stage.stage_name)
		)
		try:
			await self.__land_area_repository.update_record(
				LandArea.id == land_area.id, stage_id=stage.id
			)
			await self.session.commit()
			return stage
		except Exception as e:
			await self.session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()
