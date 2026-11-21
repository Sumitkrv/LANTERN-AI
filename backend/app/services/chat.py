from time import perf_counter

from starlette.concurrency import run_in_threadpool

from app.schemas import ChatRequest, ChatResponse, ResponseMetadata
from app.services.litellm_gateway import LiteLLMGateway
from app.services.sessions import SessionService


class ChatService:
    def __init__(self, sessions: SessionService, gateway: LiteLLMGateway) -> None:
        self.sessions = sessions
        self.gateway = gateway

    async def respond(
        self, request: ChatRequest, simulation: dict[str, int], started_at: float
    ) -> ChatResponse:
        async with self.sessions.lock(request.session_id):
            prompt, messages = await self.sessions.prepare(request)
            result = await self.gateway.resolve(messages, simulation)
            reply = result.inference.reply
            metadata = ResponseMetadata(
                resolution_source="LLM_CACHE" if result.key_id is None else "LIVE_INFERENCE",
                model=self.gateway.settings.model,
                latency_ms=int((perf_counter() - started_at) * 1000),
                input_tokens=result.inference.input_tokens,
                output_tokens=result.inference.output_tokens,
                key_id=result.key_id,
                fallback_attempts=result.fallback_attempts,
            )
            await run_in_threadpool(
                self.sessions.repository.save_turn, request.session_id, prompt, request.message,
                reply, metadata,
            )
            return ChatResponse(session_id=request.session_id, reply=reply, metadata=metadata)
