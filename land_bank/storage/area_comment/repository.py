from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from infrastructure.database.model import AreaComment
from infrastructure.repository.sqlalchemy_repository import SQLAlchemyRepository

__all__ = [
    'AreaCommentRepository'
]


class AreaCommentRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(AreaComment)

    async def get_comment(
            self,
            session: AsyncSession,
            *filters
    ) -> AreaComment:
        return await self.get_record(session, *filters)

    async def create_comment(
            self,
            session: AsyncSession,
            **values_set
    ) -> AreaComment:
        comment: AreaComment = await self.create_record(
            session, **values_set)
        return await self.get_record_with_relationships(
            session,
            filters=[AreaComment.id == comment.id],
            options=[selectinload(AreaComment.employee)]
        )

    async def edit_comment(
            self,
            session: AsyncSession,
            comment_id: UUID,
            **values_set
    ) -> AreaComment:
        """
        Изменяет комментарий и возвращает его
        :param session: Сессия БД
        :param comment_id: ID комментария
        :param values_set: Обновленные значения для комментария
        :return: Обновленный комментарий
        """
        updated_comment: AreaComment = await self.update_record(
            session, AreaComment.id == comment_id, **values_set)
        return await self.get_record_with_relationships(
            session,
            filters=[AreaComment.id == updated_comment.id],
            options=[selectinload(AreaComment.employee)]
        )

    async def delete_comment(
            self,
            session: AsyncSession,
            area_comment: AreaComment) -> None:
        await self.delete_record(session, area_comment)
