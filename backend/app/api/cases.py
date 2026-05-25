from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_cases():
    # TODO: Phase 6 — Case Management
    return {"cases": []}


@router.post("/")
async def create_case():
    # TODO: Phase 6 — Case Management
    return {"id": "placeholder"}
