from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.cases import CaseCreate, CaseUpdate, CaseResponse, GraphStateResponse
from app.schemas.entities import NodeResponse, EdgeResponse
from app.services import case_service

router = APIRouter()


def _build_case_response(case, node_count: int = 0) -> CaseResponse:
    """Build a CaseResponse from an ORM Case, injecting node_count."""
    data = CaseResponse.model_validate(case)
    # model_validate populates node_count=0 by default; override if we have it
    return data.model_copy(update={"node_count": node_count})


@router.get("/", response_model=list[CaseResponse])
async def list_cases(db: AsyncSession = Depends(get_db)) -> list[CaseResponse]:
    cases = await case_service.get_all_cases(db)
    return [_build_case_response(c) for c in cases]


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    data: CaseCreate,
    db: AsyncSession = Depends(get_db),
) -> CaseResponse:
    case = await case_service.create_case(db, data)
    await case_service.add_audit_log(
        db,
        case_id=case.id,
        event_type="case_created",
        metadata={"name": case.name},
    )
    return _build_case_response(case)


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CaseResponse:
    case = await case_service.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    node_count = len(case.nodes) if case.nodes else 0
    return _build_case_response(case, node_count=node_count)


@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: uuid.UUID,
    data: CaseUpdate,
    db: AsyncSession = Depends(get_db),
) -> CaseResponse:
    case = await case_service.update_case(db, case_id, data)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    await case_service.add_audit_log(
        db,
        case_id=case.id,
        event_type="case_updated",
        metadata={"updated_fields": data.model_dump(exclude_none=True)},
    )
    return _build_case_response(case)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await case_service.delete_case(db, case_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")


@router.get("/{case_id}/graph", response_model=GraphStateResponse)
async def get_graph(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> GraphStateResponse:
    # Verify case exists
    case = await case_service.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    state = await case_service.get_graph_state(db, case_id)
    return GraphStateResponse(
        nodes=[NodeResponse.model_validate(n) for n in state["nodes"]],
        edges=[EdgeResponse.model_validate(e) for e in state["edges"]],
    )


@router.get("/{case_id}/audit")
async def get_audit_log(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    case = await case_service.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    logs = await case_service.get_audit_logs(db, case_id)
    return [
        {
            "id": str(log.id),
            "event_type": log.event_type,
            "entity_type": log.entity_type,
            "entity_value": log.entity_value,
            "transform_name": log.transform_name,
            "metadata": log.metadata_,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
