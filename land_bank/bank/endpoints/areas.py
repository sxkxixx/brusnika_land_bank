from typing import Optional, Any, List

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends

from auth import AuthenticationDependency
from auth.models import Employee
from bank.schemas import SortParams, LimitOffset, CadastralLandAreaRequestDTO, \
	ObjectOwnerRequestDTO, AreaBuildingRequestDTO, \
	CadastralLandAreaRelatedResponseDTO
from core import rpc_exceptions
from layers import land_area_service, LandAreaService

areas_endpoint = jsonrpc.Entrypoint(path='/api/v1/areas', tags=['AREAS'])


@areas_endpoint.method(errors=[rpc_exceptions.AuthenticationError])
async def select_land_area(
		limit_offset: LimitOffset,
		sort_params: Optional[SortParams] = None,
		employee: Employee = Depends(AuthenticationDependency()),
		_land_area_service: LandAreaService = Depends(land_area_service)
) -> Any:
	# TODO написать полностью после того как узнаю что должно отображаться
	land_areas = await _land_area_service.get_ordered_lands(
		limit_offset, sort_params
	)


@areas_endpoint.method(errors=[rpc_exceptions.AuthenticationError])
async def create_cadastral_land_area(
		land_area: CadastralLandAreaRequestDTO,
		area_owners: List[Optional[ObjectOwnerRequestDTO]],
		buildings: List[Optional[AreaBuildingRequestDTO]],
		_land_area_service: LandAreaService = Depends(land_area_service),
		# employee: Employee = Depends(AuthenticationDependency()),
) -> CadastralLandAreaRelatedResponseDTO:
	land_area = await _land_area_service.create_land_area(
		land_area, area_owners, buildings,
	)
	return CadastralLandAreaRelatedResponseDTO.model_validate(
		land_area, from_attributes=True
	)
