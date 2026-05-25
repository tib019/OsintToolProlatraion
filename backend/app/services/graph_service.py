from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.graph import GraphNode, GraphEdge
from app.schemas.entities import NodeCreate, EdgeCreate


async def get_node(db: AsyncSession, node_id: uuid.UUID) -> Optional[GraphNode]:
    result = await db.execute(select(GraphNode).where(GraphNode.id == node_id))
    return result.scalar_one_or_none()


async def add_node(
    db: AsyncSession, case_id: uuid.UUID, data: NodeCreate
) -> GraphNode:
    now = datetime.now(timezone.utc)
    node = GraphNode(
        case_id=case_id,
        entity_type=data.entity_type.value,
        value=data.value,
        label=data.label,
        properties=data.properties or {},
        pos_x=data.position.x if data.position else None,
        pos_y=data.position.y if data.position else None,
        created_at=now,
    )
    db.add(node)
    await db.commit()
    await db.refresh(node)
    return node


async def remove_node(
    db: AsyncSession, case_id: uuid.UUID, node_id: uuid.UUID
) -> bool:
    result = await db.execute(
        select(GraphNode).where(
            GraphNode.id == node_id,
            GraphNode.case_id == case_id,
        )
    )
    node = result.scalar_one_or_none()
    if node is None:
        return False

    # Delete all connected edges first
    edges_result = await db.execute(
        select(GraphEdge).where(
            GraphEdge.case_id == case_id,
            or_(
                GraphEdge.source_id == node_id,
                GraphEdge.target_id == node_id,
            ),
        )
    )
    for edge in edges_result.scalars().all():
        await db.delete(edge)

    await db.delete(node)
    await db.commit()
    return True


async def add_edge(
    db: AsyncSession, case_id: uuid.UUID, data: EdgeCreate
) -> GraphEdge:
    now = datetime.now(timezone.utc)
    edge = GraphEdge(
        case_id=case_id,
        source_id=data.source_id,
        target_id=data.target_id,
        label=data.label,
        transform_name=data.transform_name,
        created_at=now,
    )
    db.add(edge)
    await db.commit()
    await db.refresh(edge)
    return edge


async def update_node_position(
    db: AsyncSession,
    case_id: uuid.UUID,
    node_id: uuid.UUID,
    x: float,
    y: float,
) -> Optional[GraphNode]:
    result = await db.execute(
        select(GraphNode).where(
            GraphNode.id == node_id,
            GraphNode.case_id == case_id,
        )
    )
    node = result.scalar_one_or_none()
    if node is None:
        return None

    node.pos_x = x
    node.pos_y = y
    db.add(node)
    await db.commit()
    await db.refresh(node)
    return node
