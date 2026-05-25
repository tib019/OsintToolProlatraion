from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api import cases, graph, transforms, export
from app.api import settings as settings_router
from app.api import websocket as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="PHANTOM OSINT Platform",
    description="Self-hosted OSINT investigation platform API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(transforms.router, prefix="/api/transforms", tags=["transforms"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])
app.include_router(websocket_router.router, tags=["websocket"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "phantom-backend"}
