import asyncio

import litellm

from conftest import send


def test_cross_session_hit_preserves_reply_and_usage(client, provider, monkeypatch):
    async def delayed(**kwargs):
        await asyncio.sleep(0.035)
        return await provider.complete(**kwargs)

    monkeypatch.setattr(litellm, "acompletion", delayed)
    first = send(client, "first").json()
    second = send(client, "second").json()
    assert len(provider.calls) == 1
    assert first["reply"] == second["reply"]
    live, cached = first["metadata"], second["metadata"]
    assert live["resolution_source"] == "LIVE_INFERENCE"
    assert cached["resolution_source"] == "LLM_CACHE"
    assert cached["key_id"] is None
    assert cached["fallback_attempts"] == 0
    assert cached["latency_ms"] < live["latency_ms"]
    assert cached["input_tokens"] == live["input_tokens"]
    assert cached["output_tokens"] == live["output_tokens"]
    assert cached["model"] == live["model"]


def test_cache_checks_full_ordered_context(client, provider):
    for session, text in [("one", "bright day"), ("two", "cloudy day")]:
        assert send(client, session, text).json()["metadata"]["resolution_source"] == "LIVE_INFERENCE"
        assert send(client, session, "Describe it.").json()["metadata"]["resolution_source"] == "LIVE_INFERENCE"

    assert send(client, "three", "bright day").json()["metadata"]["resolution_source"] == "LLM_CACHE"
    assert send(client, "three", "Describe it.").json()["metadata"]["resolution_source"] == "LLM_CACHE"
    assert len(provider.calls) == 4


def test_system_prompt_changes_cache_identity(client, provider):
    first = send(client, "one", system_prompt="Be succinct.")
    other = send(client, "two", system_prompt="Give more detail.")
    retried = send(client, "three", system_prompt="Be succinct.")
    assert first.json()["metadata"]["resolution_source"] == "LIVE_INFERENCE"
    assert other.json()["metadata"]["resolution_source"] == "LIVE_INFERENCE"
    assert retried.json()["metadata"]["resolution_source"] == "LLM_CACHE"
    assert len(provider.calls) == 2
