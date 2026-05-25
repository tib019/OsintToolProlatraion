from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def placeholder():
    return {"status": "not yet implemented"}
