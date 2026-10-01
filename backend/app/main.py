from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.artifacts import router as artifacts_router
from app.api.agent import router as agent_router
from app.api.brands import router as brands_router
from app.api.brand_state import router as brand_state_router
from app.api.conversations import router as conversations_router
from app.api.proposals import router as proposals_router
from app.api.history import router as history_router
from app.api.research import router as research_router
from app.api.assets import router as assets_router
from app.api.documents import router as documents_router
from app.api.export import router as export_router
from app.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(auth_router)
app.include_router(artifacts_router)
app.include_router(agent_router)
app.include_router(brands_router)
app.include_router(brand_state_router)
app.include_router(conversations_router)
app.include_router(proposals_router)
app.include_router(history_router)
app.include_router(research_router)
app.include_router(assets_router)
app.include_router(documents_router)
app.include_router(export_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }
