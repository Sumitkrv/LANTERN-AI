from dataclasses import dataclass, field
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
import litellm


class UpstreamStatus(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code


@dataclass
class Provider:
    calls: list[dict] = field(default_factory=list)
    failures: dict[str, int] = field(default_factory=dict)

    async def complete(self, **kwargs):
        self.calls.append(kwargs)
        if status := self.failures.get(kwargs["api_key"]):
            raise UpstreamStatus(status)
        messages = kwargs["messages"]
        reply = "Test answer: " + messages[-1]["content"]
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=reply))],
            usage=SimpleNamespace(
                prompt_tokens=sum(len(message["content"].split()) for message in messages),
                completion_tokens=len(reply.split()),
            ),
        )


@pytest.fixture
def provider(monkeypatch):
    upstream = Provider()
    monkeypatch.setattr(litellm, "acompletion", upstream.complete)
    return upstream


@pytest.fixture
def settings(tmp_path):
    return Settings(
        keys=("test-first", "test-second"),
        database_url=f"sqlite:///{tmp_path / 'lantern.db'}",
        enable_failure_simulation=True,
    )


@pytest.fixture
def client(settings, provider):
    with TestClient(create_app(settings)) as test_client:
        yield test_client


def send(client, session="first", message="How do fogbows form?", **kwargs):
    return client.post("/chat", json={"session_id": session, "message": message, **kwargs})


def simulate(client, header, session="first", message="How do fogbows form?"):
    return client.post(
        "/chat", json={"session_id": session, "message": message},
        headers={"X-Simulate-Failure": header},
    )
