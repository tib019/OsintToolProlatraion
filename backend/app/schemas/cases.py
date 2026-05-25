from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.entities import NodeResponse, EdgeResponse


class CaseCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    tags: list[str] = []


class CaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    notes_md: Optional[str] = None


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str]
    tags: list[str]
    notes_md: Optional[str]
    created_at: datetime
    updated_at: datetime
    node_count: int = 0


class GraphStateResponse(BaseModel):
    nodes: list[NodeResponse]
    edges: list[EdgeResponse]
