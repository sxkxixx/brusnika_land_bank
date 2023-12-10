from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr
from typing import Optional, List

__all__ = [
    'ObjectOwnerRequestDTO',
    'CadastralLandAreaRequestDTO',
    'AreaBuildingRequestDTO',
    'CadastralLandAreaRelatedResponseDTO'
]


class StageResponseDTO(BaseModel):
    id: UUID
    stage_name: str


class StatusResponseDTO(BaseModel):
    id: UUID
    status_name: str


class ObjectOwnerRequestDTO(BaseModel):
    owner_name: str
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: str
    location: Optional[str] = None
    person_type: str
    # addition_mark: Optional[str] = None


class ObjectOwnerResponseDTO(ObjectOwnerRequestDTO):
    id: UUID
    land_area_id: UUID


class AreaBuildingRequestDTO(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    commissioning_year: str


class AreaBuildingResponseDTO(AreaBuildingRequestDTO):
    id: UUID
    land_area_id: UUID


class CadastralLandAreaRequestDTO(BaseModel):
    cadastral_number: str
    area_category: str
    area_square: float
    search_channel: str


class CadastralLandAreaRelatedResponseDTO(CadastralLandAreaRequestDTO):
    id: UUID
    entered_at_base: datetime
    working_status_id: UUID
    stage_id: UUID

    stage: 'StageResponseDTO'
    status: 'StatusResponseDTO'
    area_buildings: Optional[List['AreaBuildingResponseDTO']] = None
    owners: Optional[List['ObjectOwnerResponseDTO']] = None
