import logging
from dataclasses import dataclass

import litellm

from app.config import Settings
from app.services.response_cache import Inference, ResponseCache


logger = logging.getLogger("lantern.gateway")


class ProvidersUnavailable(Exception):
    pass


class ProviderRejected(Exception):
    pass


@dataclass(frozen=True)
class Resolution:
    inference: Inference
    key_id: str | None = None
    fallback_attempts: int = 0


def is_retryable(exc: Exception) -> bool:
    if isinstance(exc, (litellm.RateLimitError, litellm.Timeout, litellm.APIConnectionError)):
        return True
    code = getattr(exc, "code", None)
    if isinstance(code, str) and code.lower() in {"insufficient_quota", "quota_exceeded", "resource_exhausted"}:
        return True
    status = getattr(exc, "status_code", None)
    # A revoked or forbidden credential can be replaced by another key.
    return isinstance(status, int) and (status in {401, 403, 408, 429} or 500 <= status < 600)


class LiteLLMGateway:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.cache = ResponseCache(settings.cache_ttl)

    async def resolve(self, messages: list[dict[str, str]], simulation: dict[str, int]) -> Resolution:
        if not self.settings.key_pool_ready:
            raise ProvidersUnavailable

        # The same LiteLLM cache is shared by all keys and sessions. A simulated call
        # skips both lookup and storage, so it always exercises the provider sequence.
        cache_key = None if simulation else self.cache.key(self.settings.model, messages)
        if cache_key is not None:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return Resolution(cached)

        for index, secret in enumerate(self.settings.keys):
            key_id = f"key_{index + 1}"
            status = simulation.get(key_id, simulation.get("*"))
            if status is not None:
                logger.info("Simulated provider failure key=%s status=%d", key_id, status)
                continue

            try:
                response = await litellm.acompletion(
                    model=self.settings.model,
                    messages=messages,
                    api_key=secret,
                    api_base=self.settings.api_base,
                    timeout=self.settings.provider_timeout,
                    num_retries=0,
                    caching=False,
                )
            except Exception as exc:
                logger.warning("Provider call failed key=%s type=%s", key_id, type(exc).__name__)
                if is_retryable(exc):
                    continue
                raise ProviderRejected from None

            choices = getattr(response, "choices", None)
            usage = getattr(response, "usage", None)
            text = choices[0].message.content if choices else None
            input_tokens = getattr(usage, "prompt_tokens", None)
            output_tokens = getattr(usage, "completion_tokens", None)
            if (
                not isinstance(text, str) or not text.strip()
                or type(input_tokens) is not int or input_tokens < 0
                or type(output_tokens) is not int or output_tokens < 0
            ):
                logger.warning("Provider returned an incomplete response key=%s", key_id)
                continue

            inference = Inference(reply=text, input_tokens=input_tokens, output_tokens=output_tokens)
            if cache_key is not None:
                self.cache.store(cache_key, inference)
            return Resolution(inference, key_id, index)

        raise ProvidersUnavailable
