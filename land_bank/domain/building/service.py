from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.model import Building
from infrastructure.exception import rpc_exceptions
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository


class BuildingService:
	def __init__(self):
		self.session: Union[AsyncSession, None] = None
		self.repository: Union[SQLAlchemyRepository, None] = None

	def set_async_session(self, session: AsyncSession):
		assert session.is_active, 'Session is not active'
		self.session: AsyncSession = session
		self.repository = SQLAlchemyRepository(session, Building)

	async def update(self, building_id, **values_set) -> Building:
		try:
			building = await self.repository.update_record(
				Building.id == building_id, **values_set
			)
			if not building:
				raise rpc_exceptions.ObjectDoesNotExistsError(
					data="Building does not exists")
			await self.session.commit()
			return building
		except Exception as e:
			await self.session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.session.close()
