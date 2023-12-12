from typing import Optional, List
from uuid import UUID

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends

from auth import AuthenticationDependency, AuthorizationDependency
from bank.models import Stage, Status
from bank.schemas import (
	LandAreaListResponseDTO,
	SortParams,
	LimitOffset,
	LandAreaRequestDTO,
	OwnerRequestDTO,
	BuildingRequestDTO,
	LandAreaRelatedResponseDTO,
	StageResponseDTO,
	StatusResponseDTO
)
from core import rpc_exceptions
from layers import land_area_service, LandAreaService

areas_endpoint = jsonrpc.Entrypoint(path='/api/v1/areas', tags=['AREAS'])


@areas_endpoint.method(
	errors=[rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
async def select_land_area(
		limit_offset: LimitOffset,
		sort_params: Optional[SortParams] = None,
		_land_area_service: LandAreaService = Depends(land_area_service)
) -> List[LandAreaListResponseDTO]:
	land_areas = await _land_area_service.get_ordered_lands(
		limit_offset, sort_params
	)
	return [
		LandAreaListResponseDTO.model_validate(land_area, from_attributes=True)
		for land_area in land_areas
	]


@areas_endpoint.method(
	errors=[rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
async def create_cadastral_land_area(
		land_area: LandAreaRequestDTO,
		area_owners: List[OwnerRequestDTO],
		buildings: List[BuildingRequestDTO],
		_land_area_service: LandAreaService = Depends(land_area_service),
) -> LandAreaRelatedResponseDTO:
	land_area = await _land_area_service.create_land_area(
		land_area, area_owners, buildings,
	)
	return LandAreaRelatedResponseDTO.model_validate(
		land_area, from_attributes=True
	)


@areas_endpoint.method(
	errors=[rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
async def update_cadastral_land_area(
		id: UUID,
		land_area: LandAreaRequestDTO,
		_land_area_service: LandAreaService = Depends(land_area_service)
) -> LandAreaRequestDTO:
	land_area = await _land_area_service.update_land_area_service(
		id=id, **land_area.model_dump()
	)
	return LandAreaRequestDTO.model_validate(land_area, from_attributes=True)


@areas_endpoint.method(
	errors=[
		rpc_exceptions.AuthorizationError,
		rpc_exceptions.AuthorizationError
	],
	dependencies=[
		Depends(AuthorizationDependency(
			permission_name='Can edit land area stage'
		))
	]
)
async def move_next_stage(
		id: UUID,
		_land_area_service: LandAreaService = Depends(land_area_service),
) -> StageResponseDTO:
	stage: Stage = await _land_area_service.change_stage(id)
	return StageResponseDTO.model_validate(stage, from_attributes=True)


@areas_endpoint.method(
	errors=[
		rpc_exceptions.AuthenticationError,
	],
	dependencies=[Depends(AuthenticationDependency())]
)
async def move_next_status(
		id: UUID,
		_land_area_service: LandAreaService = Depends(land_area_service)
) -> StatusResponseDTO:
	status: Status = await _land_area_service.change_status(id)
	return StatusResponseDTO.model_validate(status, from_attributes=True)
