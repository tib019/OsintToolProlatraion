from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.websocket_manager import ws_manager
from app.schemas.entities import NodeCreate, NodeResponse, EdgeCreate, EdgeResponse
from app.services import case_service, graph_service

router = APIRouter()


class NodePositionUpdate(BaseModel):
    x: float
    y: float


@router.post("/{case_id}/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def add_node(
    case_id: uuid.UUID,
    data: NodeCreate,
    db: AsyncSession = Depends(get_db),
) -> NodeResponse:
    case = await case_service.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    node = await graph_service.add_node(db, case_id, data)

    # Persist audit log
    await case_service.add_audit_log(
        db,
        case_id=case_id,
        event_type="node_added",
        entity_type=node.entity_type,
        entity_value=node.value,
        metadata={"node_id": str(node.id), "label": node.label},
    )

    response = NodeResponse.model_validate(node)

    # Broadcast to WS subscribers
    await ws_manager.broadcast(
        str(case_id),
        "node_added",
        response.model_dump(mode="json"),
    )

    return response


@router.delete(
    "/{case_id}/nodes/{node_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_node(
    case_id: uuid.UUID,
    node_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await graph_service.remove_node(db, case_id, node_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    await case_service.add_audit_log(
        db,
        case_id=case_id,
        event_type="node_removed",
        metadata={"node_id": str(node_id)},
    )

    await ws_manager.broadcast(
        str(case_id),
        "node_removed",
        {"node_id": str(node_id)},
    )


@router.post("/{case_id}/edges", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
async def add_edge(
    case_id: uuid.UUID,
    data: EdgeCreate,
    db: AsyncSession = Depends(get_db),
) -> EdgeResponse:
    case = await case_service.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # Validate source and target nodes exist and belong to this case
    source = await graph_service.get_node(db, data.source_id)
    if source is None or source.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source node not found"
        )

    target = await graph_service.get_node(db, data.target_id)
    if target is None or target.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target node not found"
        )

    edge = await graph_service.add_edge(db, case_id, data)

    await case_service.add_audit_log(
        db,
        case_id=case_id,
        event_type="edge_added",
        transform_name=edge.transform_name,
        metadata={
            "edge_id": str(edge.id),
            "source_id": str(edge.source_id),
            "target_id": str(edge.target_id),
            "label": edge.label,
        },
    )

    response = EdgeResponse.model_validate(edge)

    await ws_manager.broadcast(
        str(case_id),
        "edge_added",
        response.model_dump(mode="json"),
    )

    return response


@router.patch("/{case_id}/nodes/{node_id}/position", response_model=NodeResponse)
async def update_node_position(
    case_id: uuid.UUID,
    node_id: uuid.UUID,
    data: NodePositionUpdate,
    db: AsyncSession = Depends(get_db),
) -> NodeResponse:
    node = await graph_service.update_node_position(db, case_id, node_id, data.x, data.y)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    response = NodeResponse.model_validate(node)

    await ws_manager.broadcast(
        str(case_id),
        "node_moved",
        {"node_id": str(node_id), "x": data.x, "y": data.y},
    )

    return response
