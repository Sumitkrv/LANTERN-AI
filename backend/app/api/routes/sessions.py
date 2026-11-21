from fastapi import APIRouter, HTTPException, Request

from app.schemas import SessionID, SessionMessages


router = APIRouter()


@router.get("/sessions/{session_id:path}/messages", response_model=SessionMessages)
async def messages(session_id: SessionID, request: Request) -> SessionMessages:
    history = await request.app.state.sessions.history(session_id)
    if history is None:
        raise HTTPException(404, "session not found")
    return history
