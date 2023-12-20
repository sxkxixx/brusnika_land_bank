from uuid import UUID

from infrastructure.exception import rpc_exceptions
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository
from infrastructure.database.model import AreaComment
from sqlalchemy.ext.asyncio import AsyncSession


class CommentService:
	def __init__(self, session: AsyncSession):
		self.__session: AsyncSession = session
		self.__repository = SQLAlchemyRepository(session, AreaComment)

	async def create_comment(self, **kwargs) -> AreaComment:
		comment: AreaComment = await self.__repository.create_record(
			**kwargs
		)
		try:
			await self.__session.commit()
			return comment
		except Exception as e:
			await self.__session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))

	async def edit_comment(
			self,
			comment_id: UUID,
			employee_id: UUID,
			comment_text: str
	):
		try:
			comment: AreaComment = await self.__repository.update_record(
				AreaComment.id == comment_id,
				AreaComment.employee_id == employee_id,
				comment_text=comment_text
			)
			await self.__session.commit()
		except Exception as e:
			await self.__session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.__session.close()

	async def delete_comment(
			self,
			area_comment_id: UUID,
			employee_id: UUID
	):
		try:
			land_area = await self.__repository.delete_record(
				AreaComment.id == area_comment_id,
				AreaComment.employee_id == employee_id
			)
			await self.__session.commit()
			return land_area
		except Exception as e:
			await self.__session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await self.__session.close()
