from typing import Optional
from uuid import UUID

from fastapi_jsonrpc import Entrypoint
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from application.auth.dependency import AuthenticationDependency
from domain.extra_data.schemas import (
	ExtraDataResponseSchema,
	ExtraDataRequestSchema,
	ExtraDataEditSchema
)
from infrastructure.database.model import ExtraAreaData
from infrastructure.database.transaction import in_transaction
from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from infrastructure.exception import rpc_exceptions
from storage.extra_data import ExtraDataRepository

router = Entrypoint('/api/v1/extra_data', tags=['EXTRA DATA'])
extra_data_repository: ExtraDataRepository = ExtraDataRepository()


# TODO: Настроить права для endpoint'ов
@router.method(
	errors=[
		rpc_exceptions.TransactionError,
		rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
@in_transaction
async def create_extra_data(
		data: ExtraDataRequestSchema,
) -> ExtraDataResponseSchema:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	data: ExtraAreaData = await extra_data_repository.create_data(
		session, **data.model_dump()
	)
	return ExtraDataResponseSchema.model_validate(data, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.TransactionError,
		rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
@in_transaction
async def edit_extra_data(
		extra_data_id: UUID,
		data: ExtraDataEditSchema,
) -> ExtraDataResponseSchema:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	data_orm: Optional[ExtraAreaData] = await extra_data_repository.get_data(
		session, ExtraAreaData.id == extra_data_id)
	if not data_orm:
		raise rpc_exceptions.ObjectNotFoundError(
			data='Area extra data does not exists')
	data_orm: ExtraAreaData = await extra_data_repository.update_data(
		session, ExtraAreaData.id == extra_data_id, **data.model_dump()
	)
	return ExtraDataResponseSchema.model_validate(data_orm, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.TransactionError,
		rpc_exceptions.AuthenticationError
	],
	dependencies=[Depends(AuthenticationDependency())]
)
@in_transaction
async def delete_extra_data(
		extra_data_id: UUID
) -> None:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	data: Optional[ExtraAreaData] = await extra_data_repository.get_data(
		session, ExtraAreaData.id == extra_data_id)
	if not data:
		raise rpc_exceptions.ObjectNotFoundError(
			data='Area extra data does not exists'
		)
	await extra_data_repository.delete_data(session, data)
	return None
