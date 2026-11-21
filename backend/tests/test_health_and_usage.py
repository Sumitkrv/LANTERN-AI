from dataclasses import replace

from fastapi.testclient import TestClient

from app.main import create_app
from conftest import send


def test_readiness_and_exact_routes(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "keys_configured": 2, "cache_enabled": True}
    for path in ["/docs", "/redoc", "/openapi.json", "/"]:
        assert client.get(path).status_code == 404


def test_readiness_requires_key_pool(settings):
    for keys in [(), ("one",), ("one", "one"), ("replace_first", "replace_second")]:
        with TestClient(create_app(replace(settings, keys=keys))) as client:
            assert client.get("/health").status_code == 503


def test_readiness_requires_database(client):
    client.app.state.database.path.unlink()
    assert client.get("/health").status_code == 503


def test_cors_for_test_hook(client):
    response = client.options(
        "/chat", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Simulate-Failure, Content-Type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_usage_is_per_request_not_cumulative(client, provider):
    first = send(client, "one", "three words here").json()["metadata"]
    second = send(client, "one", "another three words").json()["metadata"]
    fresh = send(client, "two", "these are different").json()["metadata"]
    assert first["input_tokens"] == fresh["input_tokens"] < second["input_tokens"]
    for metadata, call in zip([first, second, fresh], provider.calls, strict=True):
        assert metadata["input_tokens"] == sum(len(m["content"].split()) for m in call["messages"])
        assert metadata["output_tokens"] == 2 + len(call["messages"][-1]["content"].split())
