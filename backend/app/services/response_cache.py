import hashlib
import json

from litellm.caching.caching import Cache
from pydantic import BaseModel, Field


class Inference(BaseModel):
    reply: str = Field(min_length=1)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)


class ResponseCache:
    def __init__(self, ttl: int) -> None:
        self.cache = Cache(type="local", ttl=ttl, default_in_memory_ttl=ttl)

    @staticmethod
    def key(model: str, messages: list[dict[str, str]]) -> str:
        encoded = json.dumps([model, messages], sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Inference | None:
        cached = self.cache.get_cache(cache_key=key, caching=True)
        return Inference.model_validate(cached) if cached is not None else None

    def store(self, key: str, response: Inference) -> None:
        self.cache.add_cache(response.model_dump(), cache_key=key, caching=True)
