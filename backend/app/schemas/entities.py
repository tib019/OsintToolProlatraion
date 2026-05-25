from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EntityType(str, Enum):
    PHONE_NUMBER = "PhoneNumber"
    EMAIL_ADDRESS = "EmailAddress"
    PERSON = "Person"
    USERNAME = "Username"
    SOCIAL_PROFILE = "SocialProfile"
    IP_ADDRESS = "IPAddress"
    DOMAIN = "Domain"
    ORGANIZATION = "Organization"
    LOCATION = "Location"
    LEAK_RECORD = "LeakRecord"


class NodePosition(BaseModel):
    x: float
    y: float


class NodeCreate(BaseModel):
    entity_type: EntityType
    value: str
    label: str
    properties: dict = {}
    position: Optional[NodePosition] = None


class NodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    entity_type: str
    value: str
    label: str
    properties: dict
    pos_x: Optional[float]
    pos_y: Optional[float]
    created_at: datetime


class EdgeCreate(BaseModel):
    source_id: UUID
    target_id: UUID
    label: str
    transform_name: str


class EdgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    source_id: UUID
    target_id: UUID
    label: str
    transform_name: str
    created_at: datetime
