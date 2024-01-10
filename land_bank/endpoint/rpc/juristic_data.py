from typing import List, Optional
from uuid import UUID

from fastapi import Depends
from fastapi_jsonrpc import Entrypoint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.auth.dependency import AuthenticationDependency
from domain.juristic_data.schemas import (
    LimitSchema,
    PermittedUseSchema,
    JuristicDataResponseDTO
)
from infrastructure.database.model import (
    LandArea,
    LandAreaLimit,
    LandAreaPermittedUse
)
from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from infrastructure.database.transaction import in_transaction
from infrastructure.exception import rpc_exceptions
from storage.land_area import LandAreaRepository
from storage.limit import LimitRepository
from storage.permitted_use import PermittedUseRepository

router = Entrypoint('/api/v1/juristic_data', tags=['JURISTIC DATA'])
land_area_repository: LandAreaRepository = LandAreaRepository()
limit_repository: LimitRepository = LimitRepository()
permitted_use_repository: PermittedUseRepository = PermittedUseRepository()


@router.method(
    errors=[rpc_exceptions.AuthenticationError],
    dependencies=[Depends(AuthenticationDependency())]
)
@in_transaction
async def get_area_juristic_data(
        land_area_id: UUID
) -> JuristicDataResponseDTO:
    session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    land_area: LandArea = await land_area_repository.get_area_with_limits_uses(
        session, land_area_id)
    return JuristicDataResponseDTO.model_validate(
        land_area, from_attributes=True
    )


@router.method(
    errors=[rpc_exceptions.AuthenticationError],
    dependencies=[Depends(AuthenticationDependency())]
)
@in_transaction
async def get_juristic_options() -> JuristicDataResponseDTO:
    session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    limits = await limit_repository.select_all(session)
    permitted_uses = await permitted_use_repository.select_all(session)
    return JuristicDataResponseDTO(
        limits=[
            LimitSchema.model_validate(_limit, from_attributes=True)
            for _limit in limits
        ],
        permitted_uses=[
            PermittedUseSchema.model_validate(use, from_attributes=True)
            for use in permitted_uses
        ]
    )


@router.method(
    errors=[rpc_exceptions.AuthenticationError],
    dependencies=[Depends(AuthenticationDependency())]
)
@in_transaction
async def update_area_juristic_data(
        land_area_id: UUID,
        limits: List[LimitSchema],
        permitted_uses: List[PermittedUseSchema]
) -> JuristicDataResponseDTO:
    session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    land_area: Optional[LandArea] = await land_area_repository.get_record(
        session, LandArea.id == land_area_id
    )
    if not land_area:
        raise rpc_exceptions.ObjectNotFoundError(
            data="No land area by this ID")
    await limit_repository.delete_from_association(
        session, LandAreaLimit.land_area_id == land_area_id)
    await permitted_use_repository.delete_from_association(
        session, LandAreaPermittedUse.land_area_id == land_area_id
    )
    limit_associations = await limit_repository.create_associations(
        session, land_area_id, limits)
    uses_associations = await permitted_use_repository.create_associations(
        session, land_area_id, permitted_uses)
    updated_land_area = await land_area_repository.get_land_area(
        session,
        filters=[
            LandArea.id == land_area_id
        ],
        options=[
            selectinload(LandArea.limits),
            selectinload(LandArea.permitted_uses)
        ]
    )
    return JuristicDataResponseDTO.model_validate(
        updated_land_area, from_attributes=True)
