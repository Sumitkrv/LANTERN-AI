"""Verify a running LANTERN API with two configured provider keys."""

import argparse
import json
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen
from uuid import uuid4


def verify(base_url: str) -> None:
    def request(path: str, payload: dict | None = None, simulation: str | None = None):
        headers = {"Accept": "application/json"}
        body = None
        if payload is not None:
            body = json.dumps(payload).encode()
            headers["Content-Type"] = "application/json"
        if simulation is not None:
            headers["X-Simulate-Failure"] = simulation

        req = Request(base_url.rstrip("/") + path, data=body, headers=headers)
        try:
            response = urlopen(req, timeout=90)
        except HTTPError as exc:
            response = exc
        with response:
            return response.code, json.load(response)

    def chat(session: str, message: str, simulation: str | None = None):
        return request("/chat", {"session_id": session, "message": message}, simulation)

    def history(session: str):
        return request(f"/sessions/{quote(session, safe='')}/messages")

    status, health = request("/health")
    assert status == 200 and health["status"] == "ok", (status, health)
    assert health["keys_configured"] >= 2 and health["cache_enabled"] is True, health
    print(f"Health verified with {health['keys_configured']} keys and an enabled cache.", flush=True)

    run = uuid4().hex[:8]
    original = f"smoke-{run}-original"
    message = f"For this conversation, my favorite fruit is a pear. Confirm in one sentence. Reference {run}."
    status, live = chat(original, message)
    assert status == 200, (status, live)
    live_meta = live["metadata"]
    assert live_meta["resolution_source"] == "LIVE_INFERENCE" and live["reply"].strip(), live
    assert live_meta["input_tokens"] > 0 and live_meta["output_tokens"] > 0, live_meta

    status, cached = chat(f"smoke-{run}-cached", message)
    assert status == 200, (status, cached)
    cache_meta = cached["metadata"]
    assert cached["reply"] == live["reply"]
    assert cache_meta["resolution_source"] == "LLM_CACHE"
    assert cache_meta["key_id"] is None and cache_meta["fallback_attempts"] == 0
    assert cache_meta["input_tokens"] == live_meta["input_tokens"]
    assert cache_meta["output_tokens"] == live_meta["output_tokens"]
    assert cache_meta["latency_ms"] < live_meta["latency_ms"]
    print(f"Live {live_meta['latency_ms']} ms → cache {cache_meta['latency_ms']} ms, identical reply and usage.", flush=True)

    status, followup = chat(original, "What is my favorite fruit? Answer with only its name.")
    assert status == 200 and "pear" in followup["reply"].lower(), (status, followup)
    assert followup["metadata"]["input_tokens"] > live_meta["input_tokens"], followup
    status, prior = history(original)
    assert status == 200 and [item["role"] for item in prior["messages"]] == [
        "user", "assistant", "user", "assistant",
    ], prior
    assert prior["messages"][-1]["metadata"] == followup["metadata"]
    print(f"Multi-turn memory and SQLite history verified for {original}.", flush=True)

    status, fallback = chat(f"smoke-{run}-fallback", message, "key_1=429")
    assert status == 200, (status, fallback)
    assert fallback["metadata"]["resolution_source"] == "LIVE_INFERENCE"
    assert fallback["metadata"]["key_id"] == "key_2"
    assert fallback["metadata"]["fallback_attempts"] == 1 and fallback["reply"].strip()
    print("Simulated 429 bypassed the existing cache and reached key_2.", flush=True)

    assert chat(original, "This turn must not be stored.", "*=429") == (
        503, {"detail": "all providers unavailable"},
    )
    assert history(original) == (200, prior)
    assert history(f"smoke-{run}-unknown") == (404, {"detail": "session not found"})
    status, invalid = chat(original, " ")
    assert status == 422 and "detail" in invalid
    assert history(original) == (200, prior)
    print("All-key failure, JSON validation and unchanged session history verified.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", nargs="?", default="http://localhost:8000")
    verify(parser.parse_args().base_url)
