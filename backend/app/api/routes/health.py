import sqlite3

from fastapi import APIRouter, HTTPException, Request

from app.schemas import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    state = request.app.state
    try:
        state.database.check()
    except sqlite3.Error:
        raise HTTPException(503, "database unavailable") from None

    if not state.settings.key_pool_ready or state.chat.gateway.cache is None:
        raise HTTPException(503, "provider key pool or cache is unavailable")

    return HealthResponse(keys_configured=len(state.settings.keys), cache_enabled=True)
