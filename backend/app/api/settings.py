from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.settings import ApiKeyCreate, ApiKeyResponse, ModuleState
from app.services import settings_service

router = APIRouter()

# In-process module enable/disable state (use DB or config file in production)
_module_states: dict[str, bool] = {}


@router.get("/api-keys", response_model=list[ApiKeyResponse])
async def list_api_keys(db: AsyncSession = Depends(get_db)) -> list[ApiKeyResponse]:
    keys = await settings_service.get_all_api_keys(db)
    return [
        ApiKeyResponse(
            service_name=k.service_name,
            is_active=k.is_active,
            is_set=bool(k.encrypted_key),
        )
        for k in keys
    ]


@router.post(
    "/api-keys",
    response_model=ApiKeyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def set_api_key(
    data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiKeyResponse:
    api_key = await settings_service.upsert_api_key(db, data.service_name, data.key)
    return ApiKeyResponse(
        service_name=api_key.service_name,
        is_active=api_key.is_active,
        is_set=True,
    )


@router.delete("/api-keys/{service_name}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_api_key(
    service_name: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await settings_service.delete_api_key(db, service_name)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key for '{service_name}' not found",
        )


@router.patch("/api-keys/{service_name}/activate", response_model=ApiKeyResponse)
async def activate_api_key(
    service_name: str,
    db: AsyncSession = Depends(get_db),
) -> ApiKeyResponse:
    api_key = await settings_service.set_api_key_active(db, service_name, True)
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key for '{service_name}' not found",
        )
    return ApiKeyResponse(
        service_name=api_key.service_name,
        is_active=api_key.is_active,
        is_set=True,
    )


@router.patch("/api-keys/{service_name}/deactivate", response_model=ApiKeyResponse)
async def deactivate_api_key(
    service_name: str,
    db: AsyncSession = Depends(get_db),
) -> ApiKeyResponse:
    api_key = await settings_service.set_api_key_active(db, service_name, False)
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key for '{service_name}' not found",
        )
    return ApiKeyResponse(
        service_name=api_key.service_name,
        is_active=api_key.is_active,
        is_set=True,
    )


@router.get("/modules", response_model=list[ModuleState])
async def list_modules() -> list[ModuleState]:
    # Known modules; check in-memory state (default: enabled)
    known_modules = [
        "phone_lookup",
        "email_lookup",
        "domain_lookup",
        "ip_lookup",
        "social_lookup",
        "leak_check",
    ]
    return [
        ModuleState(name=m, enabled=_module_states.get(m, True))
        for m in known_modules
    ]


@router.patch("/modules/{module_name}", response_model=ModuleState)
async def update_module_state(
    module_name: str,
    data: ModuleState,
) -> ModuleState:
    _module_states[module_name] = data.enabled
    return ModuleState(name=module_name, enabled=data.enabled)
