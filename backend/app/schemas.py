from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints


SessionID = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=128)]
MessageText = Annotated[
    str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=4000)
]


class ChatRequest(BaseModel):
    session_id: SessionID
    message: MessageText
    system_prompt: Annotated[str, StringConstraints(strict=True)] | None = None


class ResponseMetadata(BaseModel):
    resolution_source: Literal["LIVE_INFERENCE", "LLM_CACHE"]
    model: str
    latency_ms: int = Field(ge=0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    key_id: str | None
    fallback_attempts: int = Field(ge=0)


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    metadata: ResponseMetadata


class UserMessage(BaseModel):
    role: Literal["user"] = "user"
    content: str


class AssistantMessage(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str
    metadata: ResponseMetadata


class SessionMessages(BaseModel):
    session_id: str
    messages: list[UserMessage | AssistantMessage]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    keys_configured: int
    cache_enabled: bool
