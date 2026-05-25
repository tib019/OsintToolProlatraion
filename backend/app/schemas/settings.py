from __future__ import annotations

from pydantic import BaseModel


class ApiKeyCreate(BaseModel):
    service_name: str
    key: str


class ApiKeyResponse(BaseModel):
    service_name: str
    is_active: bool
    is_set: bool


class ModuleState(BaseModel):
    name: str
    enabled: bool
