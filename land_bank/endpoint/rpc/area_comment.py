from uuid import UUID

from fastapi import Depends
from fastapi_jsonrpc import Entrypoint
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dependency import AuthenticationDependency
from infrastructure.database.model import AreaComment, Employee
from infrastructure.exception import rpc_exceptions
from infrastructure.database.session import async_session_generator
from domain.area_comment import (
	AreaCommentRelatedResponseDTO,
	AreaCommentRequestDTO,
	AreaCommentResponseDTO, CommentService
)

router = Entrypoint(
	path='/api/v1/area_comment',
	tags=['AREA COMMENT']
)


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.TransactionError
	]
)
async def upload_area_comment(
		comment: AreaCommentRequestDTO,
		employee: Employee = Depends(AuthenticationDependency()),
		session: AsyncSession = Depends(async_session_generator)
) -> AreaCommentResponseDTO:
	comment_service: CommentService = CommentService(session)
	area_comment: AreaComment = await comment_service.create_comment(
		employee_id=employee.id,
		**comment.model_dump()
	)
	return AreaCommentResponseDTO.model_validate(
		area_comment,
		from_attributes=True
	)


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.TransactionError
	]
)
async def edit_area_comment(
		comment_id: UUID,
		comment_text: str,
		session: AsyncSession = Depends(async_session_generator),
		employee: Employee = Depends(AuthenticationDependency()),
) -> AreaCommentResponseDTO:
	comment_service: CommentService = CommentService(session)
	area_comment = await comment_service.edit_comment(
		comment_id, employee.id,
		comment_text=comment_text
	)
	return AreaCommentResponseDTO.model_validate(
		area_comment,
		from_attributes=True
	)


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.TransactionError
	]
)
async def delete_area_comment(
		comment_id: UUID,
		employee: Employee = Depends(AuthenticationDependency()),
		session: AsyncSession = Depends(async_session_generator)
) -> None:
	_comment_service: CommentService = CommentService(session)
	await _comment_service.delete_comment(comment_id, employee.id)
