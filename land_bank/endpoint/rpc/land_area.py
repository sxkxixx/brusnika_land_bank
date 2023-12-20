from uuid import UUID
import fastapi_jsonrpc as jsonrpc
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dependency import AuthenticationDependency

from domain.land_area.service import LandAreaService
from domain.land_area.schema import *
from domain.request_params.schema import *
from infrastructure.exception import rpc_exceptions
from infrastructure.database.session import async_session_generator

router = jsonrpc.Entrypoint(path='/api/v1/areas', tags=['AREAS'])


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
async def select_land_area(
		limit_offset: LimitOffset,
		sort_params: Optional[SortParams] = None,
		session: AsyncSession = Depends(async_session_generator)
) -> List[LandAreaListResponseDTO]:
	land_area_service = LandAreaService(session)
	land_areas = await land_area_service.get_ordered_lands(
		limit_offset, sort_params
	)
	return [
		LandAreaListResponseDTO.model_validate(land_area, from_attributes=True)
		for land_area in land_areas
	]


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.ObjectDoesNotExistsError
	],
	dependencies=[Depends(AuthenticationDependency())]
)
async def get_land_area(
		id: UUID,
		session: AsyncSession = Depends(async_session_generator)
) -> LandAreaRelatedResponseDTO:
	land_area_service: LandAreaService = LandAreaService(session)
	land_area = await land_area_service.get_area_by_id(id)
	if not land_area:
		raise rpc_exceptions.ObjectDoesNotExistsError(
			data='No such land area by this id')
	return LandAreaRelatedResponseDTO.model_validate(
		land_area,
		from_attributes=True
	)


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
async def create_cadastral_land_area(
		land_area: LandAreaRequestDTO,
		area_owners: List[OwnerRequestDTO],
		buildings: List[BuildingRequestDTO],
		session: AsyncSession = Depends(async_session_generator),
) -> LandAreaRelatedResponseDTO:
	land_area_service: LandAreaService = LandAreaService(session)
	land_area = await land_area_service.create_land_area(
		land_area, area_owners, buildings,
	)
	return LandAreaRelatedResponseDTO.model_validate(
		land_area, from_attributes=True
	)


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
	dependencies=[Depends(AuthenticationDependency())]
)
async def update_cadastral_land_area(
		id: UUID,
		land_area: LandAreaRequestDTO,
		session: AsyncSession = Depends(async_session_generator),
) -> LandAreaRequestDTO:
	land_area_service: LandAreaService = LandAreaService(session)
	land_area = await land_area_service.update_land_area_service(
		id=id, **land_area.model_dump()
	)
	return LandAreaRequestDTO.model_validate(land_area, from_attributes=True)
