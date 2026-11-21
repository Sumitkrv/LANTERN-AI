from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from conftest import send, simulate


@pytest.mark.parametrize("status", [429, 500, 502, 503])
def test_simulated_failure_is_request_scoped(client, provider, status):
    result = simulate(client, f"key_1={status}")
    assert result.status_code == 200
    assert result.json()["metadata"]["key_id"] == "key_2"
    assert result.json()["metadata"]["fallback_attempts"] == 1
    assert result.json()["metadata"]["resolution_source"] == "LIVE_INFERENCE"
    assert provider.calls[0]["api_key"] == "test-second"
    normal = send(client, session="fresh")
    assert normal.json()["metadata"]["key_id"] == "key_1"


@pytest.mark.parametrize("header", ["*=429", "key_1=429,key_2=500"])
def test_all_keys_simulated_unavailable(client, provider, header):
    response = simulate(client, header)
    assert (response.status_code, response.json()) == (503, {"detail": "all providers unavailable"})
    assert client.get("/sessions/first/messages").status_code == 404
    assert not provider.calls


def test_cached_reply_does_not_mask_simulation(client, provider):
    assert send(client).status_code == 200
    result = simulate(client, "key_1=429", session="another")
    assert result.status_code == 200
    assert result.json()["metadata"]["key_id"] == "key_2"
    assert simulate(client, "*=429", session="third").status_code == 503
    assert send(client, "fourth").json()["metadata"]["resolution_source"] == "LLM_CACHE"
    assert len(provider.calls) == 2


def test_disabled_simulation_ignores_header(settings, provider):
    with TestClient(create_app(replace(settings, enable_failure_simulation=False))) as client:
        result = simulate(client, "*=429")
        assert result.status_code == 200
        assert result.json()["metadata"]["key_id"] == "key_1"
        assert len(provider.calls) == 1


@pytest.mark.parametrize("status", [429, 500, 502, 503, 504])
def test_provider_status_fails_over(client, provider, status):
    provider.failures["test-first"] = status
    result = send(client)
    assert result.status_code == 200
    assert result.json()["metadata"]["key_id"] == "key_2"
    assert result.json()["metadata"]["fallback_attempts"] == 1
    assert [call["api_key"] for call in provider.calls] == ["test-first", "test-second"]
    assert all(call["num_retries"] == 0 for call in provider.calls)


def test_all_real_attempts_failing(client, provider):
    provider.failures = {"test-first": 429, "test-second": 502}
    response = send(client)
    assert (response.status_code, response.json()) == (503, {"detail": "all providers unavailable"})
    assert client.get("/sessions/first/messages").status_code == 404


@pytest.mark.parametrize("header", ["key_3=500", "key_1=403", "", "key_1=500,"])
def test_invalid_simulation_is_rejected(client, provider, header):
    response = simulate(client, header)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert not provider.calls


def test_nonretryable_response_is_safe_json(client, provider):
    provider.failures["test-first"] = 400
    response = send(client)
    assert response.status_code == 502
    assert response.json() == {"detail": "model provider could not complete the request"}
    assert len(provider.calls) == 1


def test_structured_quota_error_fails_over(client, provider, monkeypatch):
    import litellm

    class QuotaExceeded(Exception):
        status_code = 400
        code = "insufficient_quota"

    async def complete(**kwargs):
        if kwargs["api_key"] == "test-first":
            raise QuotaExceeded
        return await provider.complete(**kwargs)

    monkeypatch.setattr(litellm, "acompletion", complete)
    result = send(client)
    assert result.status_code == 200
    assert result.json()["metadata"]["key_id"] == "key_2"
    assert result.json()["metadata"]["fallback_attempts"] == 1
