from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TransformInfo(BaseModel):
    name: str
    description: str
    input_types: list[str]
    output_types: list[str]
    timeout: int
    rate_limit: int


class TransformRunRequest(BaseModel):
    case_id: UUID
    node_id: UUID
    transform_name: str


class TransformRunResponse(BaseModel):
    job_id: str
    status: str = "queued"


class TransformJobStatus(BaseModel):
    job_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
