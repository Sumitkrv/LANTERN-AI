import pytest

from conftest import send


@pytest.mark.parametrize(
    "body",
    [
        {"session_id": "id", "message": ""},
        {"session_id": "id", "message": " \n\t "},
        {"message": "hello"},
        {"session_id": "id"},
        {"session_id": "", "message": "hello"},
        {"session_id": "id", "message": "a" * 4001},
        {"session_id": "a" * 129, "message": "hello"},
        {"session_id": 4, "message": "hello"},
        {"session_id": "id", "message": 4},
        {"session_id": "id", "message": "hello", "system_prompt": ["hello"]},
    ],
)
def test_invalid_request(client, provider, body):
    result = client.post("/chat", json=body)
    assert result.status_code == 422
    assert "detail" in result.json()
    assert not provider.calls


def test_malformed_json(client):
    result = client.post("/chat", content="{", headers={"Content-Type": "application/json"})
    assert result.status_code == 422
    assert result.json()["detail"][0]["type"] == "json_invalid"


def test_max_length_after_trimming(client, provider):
    response = send(client, "s" * 128, "  " + "a" * 4000 + "\n")
    assert response.status_code == 200
    assert provider.calls[0]["messages"][-1]["content"] == "a" * 4000
    result = response.json()
    assert result["session_id"] == "s" * 128
    assert result["reply"].strip()
    assert set(result["metadata"]) == {
        "resolution_source", "model", "latency_ms", "input_tokens", "output_tokens",
        "key_id", "fallback_attempts",
    }
    assert type(result["metadata"]["latency_ms"]) is int
