from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.graph import GraphNode, GraphEdge
from app.models.audit import AuditLog
from app.schemas.cases import CaseCreate, CaseUpdate


async def get_all_cases(db: AsyncSession) -> list[Case]:
    result = await db.execute(select(Case).order_by(Case.created_at.desc()))
    return list(result.scalars().all())


async def get_case(db: AsyncSession, case_id: uuid.UUID) -> Optional[Case]:
    result = await db.execute(
        select(Case)
        .where(Case.id == case_id)
        .options(selectinload(Case.nodes), selectinload(Case.edges))
    )
    return result.scalar_one_or_none()


async def create_case(db: AsyncSession, data: CaseCreate) -> Case:
    now = datetime.now(timezone.utc)
    case = Case(
        name=data.name,
        description=data.description or "",
        tags=data.tags or [],
        created_at=now,
        updated_at=now,
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return case


async def update_case(
    db: AsyncSession, case_id: uuid.UUID, data: CaseUpdate
) -> Optional[Case]:
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if case is None:
        return None

    if data.name is not None:
        case.name = data.name
    if data.description is not None:
        case.description = data.description
    if data.tags is not None:
        case.tags = data.tags
    if data.notes_md is not None:
        case.notes_md = data.notes_md

    case.updated_at = datetime.now(timezone.utc)
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return case


async def delete_case(db: AsyncSession, case_id: uuid.UUID) -> bool:
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if case is None:
        return False
    await db.delete(case)
    await db.commit()
    return True


async def get_graph_state(db: AsyncSession, case_id: uuid.UUID) -> dict:
    nodes_result = await db.execute(
        select(GraphNode).where(GraphNode.case_id == case_id).order_by(GraphNode.created_at)
    )
    nodes = list(nodes_result.scalars().all())

    edges_result = await db.execute(
        select(GraphEdge).where(GraphEdge.case_id == case_id).order_by(GraphEdge.created_at)
    )
    edges = list(edges_result.scalars().all())

    return {"nodes": nodes, "edges": edges}


async def add_audit_log(
    db: AsyncSession,
    case_id: uuid.UUID,
    event_type: str,
    entity_type: Optional[str] = None,
    entity_value: Optional[str] = None,
    transform_name: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> AuditLog:
    log = AuditLog(
        case_id=case_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_value=entity_value,
        transform_name=transform_name,
        metadata_=metadata or {},
        created_at=datetime.now(timezone.utc),
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def get_audit_logs(db: AsyncSession, case_id: uuid.UUID) -> list[AuditLog]:
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.case_id == case_id)
        .order_by(AuditLog.created_at.desc())
    )
    return list(result.scalars().all())
