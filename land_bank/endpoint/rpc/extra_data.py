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
from domain.extra_data.service import ExtraDataService
from infrastructure.database.model import ExtraAreaData
from infrastructure.database.session import async_session_generator
from infrastructure.exception import rpc_exceptions

router = Entrypoint('/api/v1/extra_data', tags=['EXTRA DATA'])
extra_data_service: ExtraDataService = ExtraDataService()


# TODO: Настроить права для endpoint'ов
@router.method(
	errors=[
		rpc_exceptions.TransactionError,
		rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
async def create_extra_data(
		data: ExtraDataRequestSchema,
		session: AsyncSession = Depends(async_session_generator)
) -> ExtraDataResponseSchema:
	extra_data_service.set_async_session(session)
	data: ExtraAreaData = await extra_data_service.create(**data.model_dump())
	return ExtraDataResponseSchema.model_validate(data, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.TransactionError,
		rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
async def edit_extra_data(
		id: UUID,
		data: ExtraDataEditSchema,
		session: AsyncSession = Depends(async_session_generator)
) -> ExtraDataResponseSchema:
	extra_data_service.set_async_session(session)
	data: ExtraAreaData = await extra_data_service.update(
		id, **data.model_dump()
	)
	return ExtraDataResponseSchema.model_validate(data, from_attributes=True)
