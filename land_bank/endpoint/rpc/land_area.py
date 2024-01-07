from uuid import UUID
from typing import Iterable
from fastapi import Depends
import fastapi_jsonrpc as jsonrpc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dependency import AuthenticationDependency

from domain.land_area.schema import *
from domain.request_params.schema import *

from infrastructure.exception import rpc_exceptions
from infrastructure.database.model import Building, LandArea, LandOwner
from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from infrastructure.database.transaction import in_transaction
from storage.building import BuildingRepository
from storage.land_area import LandAreaRepository
from storage.owner import OwnerRepository

router = jsonrpc.Entrypoint(
	path='/api/v1/areas',
	tags=['AREAS'],
	dependencies=[
		Depends(AuthenticationDependency())
	]
)
owner_repository: OwnerRepository = OwnerRepository()
building_repository: BuildingRepository = BuildingRepository()
land_area_repository: LandAreaRepository = LandAreaRepository()


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
)
@in_transaction
async def select_land_area(
		limit_offset: LimitOffset,
		sort_params: Optional[SortParams] = None,
) -> List[LandAreaListResponseDTO]:

	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	land_areas: Iterable[
		LandArea] = await land_area_repository.get_ordered_lands(
		session, limit_offset, sort_params)

	return [
		LandAreaListResponseDTO.model_validate(land_area, from_attributes=True)
		for land_area in land_areas
	]


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.ObjectNotFoundError
	],
)
@in_transaction
async def get_land_area(
		land_area_id: UUID
) -> LandAreaRelatedResponseDTO:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	land_area: Optional[LandArea] = await land_area_repository.get_land_area_relations(
		session, land_area_id)
	if not land_area:
		raise rpc_exceptions.ObjectNotFoundError(
			data='No such land area by this id'
		)

	return LandAreaRelatedResponseDTO.model_validate(
		land_area,
		from_attributes=True
	)


@router.method(
	errors=[rpc_exceptions.AuthenticationError],
)
@in_transaction
async def create_cadastral_land_area(
		land_area: LandAreaRequestDTO,
		area_owners: List[OwnerRequestDTO],
		buildings: List[BuildingRequestDTO],
) -> LandAreaRelatedResponseDTO:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	land_area_orm: LandArea = await land_area_repository.create_land_area(
		session, **land_area.model_dump())
	area_owners_list: List[LandOwner] = await owner_repository.create_owners(
		session, land_area_orm.id, area_owners)
	building_list: List[Building] = await building_repository.create_buildings(
		session, land_area_orm.id, buildings
	)
	rel_land_area: LandArea = await land_area_repository.get_land_area(
		session,
		filters=[LandArea.id == land_area_orm.id],
		options=[
			selectinload(LandArea.area_buildings),
			selectinload(LandArea.owners),
			selectinload(LandArea.comments),
			selectinload(LandArea.extra_data)
		]
	)
	return LandAreaRelatedResponseDTO.model_validate(
		rel_land_area, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.AuthenticationError,
		rpc_exceptions.TransactionError
	],
)
@in_transaction
async def update_cadastral_land_area(
		land_area_id: UUID,
		land_area: LandAreaRequestDTO,
) -> LandAreaRequestDTO:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	land_area: LandArea = await land_area_repository.update_land_area(
		session, land_area_id, **land_area.model_dump()
	)
	return LandAreaRequestDTO.model_validate(land_area, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.TransactionError,
		rpc_exceptions.AuthenticationError
	],
)
@in_transaction
async def update_owner(
		owner_id: UUID,
		owner: OwnerRequestDTO,
) -> OwnerResponseDTO:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	orm_owner: LandOwner = await owner_repository.update_record(
		session, owner_id, **owner.model_dump())
	return OwnerResponseDTO.model_validate(orm_owner, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.TransactionError,
		rpc_exceptions.AuthenticationError
	],
)
@in_transaction
async def update_building(
		building_id: UUID,
		building: BuildingRequestDTO,
) -> BuildingResponseDTO:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	orm_building: Building = await building_repository.update_building(
		session, building_id, **building.model_dump())
	return BuildingResponseDTO.model_validate(
		orm_building, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.TransactionError,
		rpc_exceptions.AuthenticationError,
	],
)
@in_transaction
async def add_owner(
		land_area_id: UUID,
		owner_schema: OwnerRequestDTO
) -> OwnerResponseDTO:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	land_area: LandArea = await land_area_repository.get_record(
		session, LandArea.id == land_area_id)
	if not land_area:
		raise rpc_exceptions.ObjectNotFoundError(
			data='No such Land Area by this id')
	owner: LandOwner = await owner_repository.create_owner(
		session, **owner_schema.model_dump(), land_area_id=land_area_id)
	return OwnerResponseDTO.model_validate(owner, from_attributes=True)


@router.method(
	errors=[
		rpc_exceptions.TransactionError,
		rpc_exceptions.AuthenticationError,
	],
)
@in_transaction
async def add_building(
		land_area_id: UUID,
		building_schema: BuildingRequestDTO
) -> BuildingResponseDTO:
	session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
	land_area: LandArea = await land_area_repository.get_record(
		session, LandArea.id == land_area_id)
	if not land_area:
		raise rpc_exceptions.ObjectNotFoundError(
			data='No such Land Area by this id')
	building: Building = await building_repository.create_building(
		session, **building_schema.model_dump(), land_area_id=land_area_id)
	return BuildingResponseDTO.model_validate(building, from_attributes=True)
