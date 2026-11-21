from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request

from app.schemas import ChatRequest, ChatResponse
from app.services.failure_simulation import InvalidSimulation, simulated_failures
from app.services.litellm_gateway import ProviderRejected, ProvidersUnavailable


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
    simulate: Annotated[str | None, Header(alias="X-Simulate-Failure")] = None,
) -> ChatResponse:
    state = request.app.state
    try:
        failures = simulated_failures(
            simulate, state.settings.enable_failure_simulation, len(state.settings.keys)
        )
        return await state.chat.respond(payload, failures, request.state.started_at)
    except InvalidSimulation:
        raise HTTPException(422, "invalid failure simulation header") from None
    except ProvidersUnavailable:
        raise HTTPException(503, "all providers unavailable") from None
    except ProviderRejected:
        raise HTTPException(502, "model provider could not complete the request") from None
