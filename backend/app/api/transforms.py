from __future__ import annotations

import uuid as uuid_module
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.websocket_manager import ws_manager
from app.schemas.transforms import (
    TransformInfo,
    TransformRunRequest,
    TransformRunResponse,
    TransformJobStatus,
)
from app.services import case_service, graph_service, settings_service
from app.services.graph_service import add_edge, add_node
from app.schemas.entities import NodeCreate, EdgeCreate, EntityType as SchemaEntityType
from app.transforms.registry import registry
from app.transforms.base import Entity, EntityType as TransformEntityType

router = APIRouter()

# In-memory job store (use Redis in production)
jobs: dict[str, dict[str, Any]] = {}


def _transform_to_info(t) -> TransformInfo:
    return TransformInfo(
        name=t.name,
        description=t.description,
        input_types=[et.value if hasattr(et, "value") else str(et) for et in t.input_types],
        output_types=[et.value if hasattr(et, "value") else str(et) for et in t.output_types],
        timeout=t.timeout,
        rate_limit=t.rate_limit,
    )


@router.get("/", response_model=list[TransformInfo])
async def list_transforms() -> list[TransformInfo]:
    return [_transform_to_info(t) for t in registry.all_transforms()]


@router.get("/entity/{entity_type}", response_model=list[TransformInfo])
async def get_transforms_for_entity(entity_type: str) -> list[TransformInfo]:
    transforms = [
        t
        for t in registry.all_transforms()
        if any(
            (et.value if hasattr(et, "value") else str(et)) == entity_type
            for et in t.input_types
        )
    ]
    return [_transform_to_info(t) for t in transforms]


@router.post("/run", response_model=TransformRunResponse)
async def run_transform(
    req: TransformRunRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> TransformRunResponse:
    # Validate case exists
    case = await case_service.get_case(db, req.case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # Validate node exists
    node = await graph_service.get_node(db, req.node_id)
    if node is None or node.case_id != req.case_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    # Validate transform exists
    transform = registry.get_by_name(req.transform_name)
    if transform is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transform '{req.transform_name}' not found",
        )

    job_id = str(uuid_module.uuid4())
    jobs[job_id] = {"status": "running", "result": None, "error": None}

    background_tasks.add_task(execute_transform, job_id, req, db)

    await case_service.add_audit_log(
        db,
        case_id=req.case_id,
        event_type="transform_queued",
        entity_type=node.entity_type,
        entity_value=node.value,
        transform_name=req.transform_name,
        metadata={"job_id": job_id, "node_id": str(req.node_id)},
    )

    return TransformRunResponse(job_id=job_id, status="queued")


@router.get("/job/{job_id}", response_model=TransformJobStatus)
async def get_job(job_id: str) -> TransformJobStatus:
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return TransformJobStatus(
        job_id=job_id,
        status=job["status"],
        result=job.get("result"),
        error=job.get("error"),
    )


async def execute_transform(
    job_id: str,
    req: TransformRunRequest,
    db: AsyncSession,
) -> None:
    """Background task: run the transform and persist results."""
    transform = registry.get_by_name(req.transform_name)
    if transform is None:
        jobs[job_id] = {
            "status": "error",
            "result": None,
            "error": f"Transform '{req.transform_name}' not found",
        }
        return

    try:
        # Get the node
        node = await graph_service.get_node(db, req.node_id)
        if node is None:
            jobs[job_id] = {
                "status": "error",
                "result": None,
                "error": "Node not found",
            }
            return

        # Retrieve API keys
        api_keys = await settings_service.get_decrypted_api_keys(db)

        # Build Entity for the transform
        try:
            entity_type = TransformEntityType(node.entity_type)
        except ValueError:
            entity_type = TransformEntityType.PERSON  # fallback

        entity = Entity(
            type=entity_type,
            value=node.value,
            properties=node.properties or {},
            label=node.label,
        )

        # Execute transform
        result = await transform.execute(entity, api_keys)

        if result.error:
            jobs[job_id] = {
                "status": "error",
                "result": None,
                "error": result.error,
            }
            await case_service.add_audit_log(
                db,
                case_id=req.case_id,
                event_type="transform_failed",
                entity_type=node.entity_type,
                entity_value=node.value,
                transform_name=req.transform_name,
                metadata={"job_id": job_id, "error": result.error},
            )
            await ws_manager.broadcast(
                str(req.case_id),
                "transform_failed",
                {"job_id": job_id, "error": result.error},
            )
            return

        # Persist result entities as nodes and edges
        new_nodes = []
        new_edges = []
        for out_entity in result.entities:
            # Create node for each result entity
            try:
                schema_entity_type = SchemaEntityType(out_entity.type.value)
            except ValueError:
                schema_entity_type = SchemaEntityType.PERSON

            node_data = NodeCreate(
                entity_type=schema_entity_type,
                value=out_entity.value,
                label=out_entity.label or out_entity.value,
                properties=out_entity.properties or {},
            )
            new_node = await add_node(db, req.case_id, node_data)
            new_nodes.append(new_node)

            # Create edge from source node to new node
            edge_data = EdgeCreate(
                source_id=req.node_id,
                target_id=new_node.id,
                label=req.transform_name,
                transform_name=req.transform_name,
            )
            new_edge = await add_edge(db, req.case_id, edge_data)
            new_edges.append(new_edge)

        job_result = {
            "nodes_created": len(new_nodes),
            "edges_created": len(new_edges),
            "duration_ms": result.duration_ms,
            "metadata": result.metadata,
            "node_ids": [str(n.id) for n in new_nodes],
            "edge_ids": [str(e.id) for e in new_edges],
        }

        jobs[job_id] = {
            "status": "completed",
            "result": job_result,
            "error": None,
        }

        await case_service.add_audit_log(
            db,
            case_id=req.case_id,
            event_type="transform_completed",
            entity_type=node.entity_type,
            entity_value=node.value,
            transform_name=req.transform_name,
            metadata={"job_id": job_id, **job_result},
        )

        await ws_manager.broadcast(
            str(req.case_id),
            "transform_completed",
            {"job_id": job_id, "result": job_result},
        )

    except Exception as exc:
        jobs[job_id] = {
            "status": "error",
            "result": None,
            "error": str(exc),
        }
        try:
            await ws_manager.broadcast(
                str(req.case_id),
                "transform_failed",
                {"job_id": job_id, "error": str(exc)},
            )
        except Exception:
            pass
