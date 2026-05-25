from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey
from app.core.encryption import encrypt, decrypt


async def get_all_api_keys(db: AsyncSession) -> list[ApiKey]:
    result = await db.execute(select(ApiKey).order_by(ApiKey.service_name))
    return list(result.scalars().all())


async def get_api_key(db: AsyncSession, service_name: str) -> Optional[ApiKey]:
    result = await db.execute(
        select(ApiKey).where(ApiKey.service_name == service_name)
    )
    return result.scalar_one_or_none()


async def upsert_api_key(
    db: AsyncSession, service_name: str, key_value: str
) -> ApiKey:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(ApiKey).where(ApiKey.service_name == service_name)
    )
    api_key = result.scalar_one_or_none()

    encrypted = encrypt(key_value)

    if api_key is None:
        api_key = ApiKey(
            service_name=service_name,
            encrypted_key=encrypted,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
    else:
        api_key.encrypted_key = encrypted
        api_key.is_active = True
        api_key.updated_at = now

    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return api_key


async def delete_api_key(db: AsyncSession, service_name: str) -> bool:
    result = await db.execute(
        select(ApiKey).where(ApiKey.service_name == service_name)
    )
    api_key = result.scalar_one_or_none()
    if api_key is None:
        return False
    await db.delete(api_key)
    await db.commit()
    return True


async def set_api_key_active(
    db: AsyncSession, service_name: str, is_active: bool
) -> Optional[ApiKey]:
    result = await db.execute(
        select(ApiKey).where(ApiKey.service_name == service_name)
    )
    api_key = result.scalar_one_or_none()
    if api_key is None:
        return None
    api_key.is_active = is_active
    api_key.updated_at = datetime.now(timezone.utc)
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return api_key


async def get_decrypted_api_keys(db: AsyncSession) -> dict[str, str]:
    """Return a mapping of service_name -> decrypted key for all active keys."""
    keys = await get_all_api_keys(db)
    result = {}
    for k in keys:
        if k.is_active:
            try:
                result[k.service_name] = decrypt(k.encrypted_key)
            except Exception:
                pass
    return result
