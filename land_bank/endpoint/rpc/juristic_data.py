from typing import Optional
from uuid import UUID
from fastapi import Depends
from fastapi_jsonrpc import Entrypoint
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dependency import AuthenticationDependency
from domain.juristic_data.schemas import (
	JuristicDataRelatedResponseDTO,
	JuristicDataRequestDTO,
	JuristicDataEditRequestDTO
)
from domain.juristic_data.service import JuristicDataService
from infrastructure.exception import rpc_exceptions
from infrastructure.database.session import async_session_generator
from infrastructure.database.model import JuristicData

router = Entrypoint('/api/v1/juristic_data', tags=['JURISTIC DATA'])
juristic_data_service: JuristicDataService = JuristicDataService()


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
	dependencies=[
		Depends(AuthenticationDependency())
	]
)
async def get_juristic_data_by_area_id(
		land_area_id: UUID,
		session: AsyncSession = Depends(async_session_generator)
) -> Optional[JuristicDataRelatedResponseDTO]:
	juristic_data_service.set_async_session(session)
	data: JuristicData = await juristic_data_service.get_by_land_area_id(
		land_area_id)
	if not data:
		return None
	return JuristicDataRelatedResponseDTO.model_validate(
		data,
		from_attributes=True
	)


@router.method(
	errors=[
		rpc_exceptions.TransactionError,
		rpc_exceptions.AuthenticationError
	],
	dependencies=[
		Depends(AuthenticationDependency())
	]
)
async def create_juristic_data(
		data: JuristicDataRequestDTO,
		session: AsyncSession = Depends(async_session_generator)
) -> JuristicDataRelatedResponseDTO:
	juristic_data_service.set_async_session(session)
	data: JuristicData = await juristic_data_service.create_data(data)
	return JuristicDataRelatedResponseDTO.model_validate(
		data, from_attributes=True
	)


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.TransactionError
	],
	dependencies=[
		# Depends(AuthenticationDependency())
	]
)
async def update_juristic_data(
		juristic_data_id: UUID,
		data: JuristicDataEditRequestDTO,
		session: AsyncSession = Depends(async_session_generator)
) -> JuristicDataRelatedResponseDTO:
	"""На данный момент работает с багом, не советую подключать"""
	# TODO: Пофиксить
	juristic_data_service.set_async_session(session)
	data: JuristicData = await juristic_data_service.update_data(
		juristic_data_id, data)
	return JuristicDataRelatedResponseDTO.model_validate(
		data, from_attributes=True)
