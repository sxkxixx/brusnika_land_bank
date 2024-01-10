from uuid import UUID

from fastapi import Depends
from fastapi_jsonrpc import Entrypoint
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dependency import AuthenticationDependency
from domain.area_comment import AreaCommentRequestDTO, AreaCommentResponseDTO
from infrastructure.database.model import AreaComment, Employee
from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from infrastructure.database.transaction import in_transaction
from infrastructure.exception import rpc_exceptions
from storage.area_comment import AreaCommentRepository

router = Entrypoint(
    path='/api/v1/area_comment',
    tags=['AREA COMMENT']
)
area_comment_repository = AreaCommentRepository()


@router.method(
    errors=[
        rpc_exceptions.AuthenticationError,
        rpc_exceptions.TransactionError
    ]
)
@in_transaction
async def upload_area_comment(
        comment: AreaCommentRequestDTO,
        employee: Employee = Depends(AuthenticationDependency()),
) -> AreaCommentResponseDTO:
    session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    area_comment: AreaComment = await area_comment_repository.create_comment(
        session, employee_id=employee.id, **comment.model_dump()
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
@in_transaction
async def edit_area_comment(
        comment_id: UUID,
        comment_text: str,
        employee: Employee = Depends(AuthenticationDependency()),
) -> AreaCommentResponseDTO:
    session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    comment: AreaComment = await area_comment_repository.get_comment(
        session, AreaComment.id == comment_id
    )
    if comment.employee_id != employee.id:
        raise rpc_exceptions.TransactionForbiddenError(
            data="Not allowed to update another owner comment")
    area_comment = await area_comment_repository.edit_comment(
        session, comment.id, comment_text=comment_text
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
@in_transaction
async def delete_area_comment(
        comment_id: UUID,
        employee: Employee = Depends(AuthenticationDependency()),
) -> None:
    session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    comment: AreaComment = await area_comment_repository.get_comment(
        session, AreaComment.id == comment_id
    )
    if comment.employee_id != employee.id:
        raise rpc_exceptions.TransactionForbiddenError(
            data="Not allowed to delete another owner comment")
    await area_comment_repository.delete_comment(session, comment)
    return None
