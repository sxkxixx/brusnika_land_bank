from typing import Iterable, List, Union
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from .schemas import JuristicDataEditRequestDTO, JuristicDataRequestDTO
from infrastructure.database.model import JuristicData, Limit, PermittedUse
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.exception import rpc_exceptions

from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository


class JuristicDataService:
	def __init__(self):
		self.session: Union[AsyncSession, None] = None
		self.data_repository: Union[SQLAlchemyRepository, None] = None
		self.limit_repository: Union[SQLAlchemyRepository, None] = None
		self.uses_repository: Union[SQLAlchemyRepository, None] = None

	def set_async_session(self, session: AsyncSession):
		self.session = session
		self.data_repository = SQLAlchemyRepository(session, JuristicData)
		self.limit_repository = SQLAlchemyRepository(session, Limit)
		self.uses_repository = SQLAlchemyRepository(session, PermittedUse)

	async def get_by_land_area_id(self, land_area_id) -> JuristicData:
		"""
		Возвращает юридическую информацию по ID земельного уастка
		:param land_area_id: ID земельного участка
		:return: JuristicData
		"""
		return await self.__get_by_filters(
			JuristicData.land_area_id == land_area_id
		)

	async def __get_by_filters(self, *filters) -> JuristicData:
		return await self.data_repository.get_record_with_relationships(
			filters=filters,
			options=[
				selectinload(JuristicData.limits),
				selectinload(JuristicData.permitted_use_list)
			]
		)

	async def create_data(
			self,
			schema: JuristicDataRequestDTO
	) -> JuristicData:
		"""Создает и возвращает созаданную юридическую информацию
		:param schema Схема данных JuristicDataRequestDTO
		"""
		try:
			juristic_data = JuristicData(
				land_area_id=schema.land_area_id,
				buildings_count=schema.buildings_count,
				owners_count=schema.owners_count,
				cadastral_cost=schema.cadastral_cost)
			juristic_data.limits = await self.__get_limit_list(schema.limits)
			juristic_data.permitted_use_list = await (
				self.__get_permitted_use_list(
					schema.permitted_use_list
				))
			self.session.add(juristic_data)
			await self.session.commit()
			return juristic_data
		except Exception as e:
			await self.session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()

	async def update_data(
			self, data_id: UUID,
			schema: JuristicDataEditRequestDTO) -> JuristicData:
		limits_schema: List = schema.limits
		permitted_uses: List = schema.permitted_use_list
		try:
			data: JuristicData = await self.__get_by_filters(
				JuristicData.id == data_id)
			data.buildings_count = schema.buildings_count
			data.owners_count = schema.owners_count
			data.cadastral_cost = schema.cadastral_cost

			data.limits = await self.__get_limit_list(limits_schema)
			data.permitted_use_list = await self.__get_permitted_use_list(
				permitted_uses)
			await self.session.merge(data)
			await self.session.commit()
			return data
		except Exception as e:
			await self.session.rollback()
			print(e)
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()

	async def __get_limit_list(self, limits) -> List[Limit]:
		result = []
		for limit in limits:
			orm_limit = await self.limit_repository.get_record(
				Limit.id == limit.id, Limit.name == limit.name
			)
			result.append(orm_limit)
		return result

	async def __get_permitted_use_list(self, permitted_uses) -> List[
		PermittedUse]:
		result = []
		for use in permitted_uses:
			orm_use = await self.limit_repository.get_record(
				PermittedUse.id == use.id, PermittedUse.name == use.name
			)
			result.append(orm_use)
		return result
