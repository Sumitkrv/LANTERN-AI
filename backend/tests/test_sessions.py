from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

from fastapi.testclient import TestClient

from app.main import create_app
from conftest import send, simulate


def test_context_order_isolation_and_session_prompt(client, provider):
    first = send(client, "one", "My codeword is amber.", system_prompt="Answer briefly.")
    assert first.status_code == 200
    assert send(client, "two", "What was the codeword?").status_code == 200
    second = send(client, "one", "What was the codeword?")
    assert second.status_code == 200
    history = client.get("/sessions/one/messages").json()
    assert history["session_id"] == "one"
    assert history["messages"] == [
        {"role": "user", "content": "My codeword is amber."},
        {"role": "assistant", "content": first.json()["reply"], "metadata": first.json()["metadata"]},
        {"role": "user", "content": "What was the codeword?"},
        {"role": "assistant", "content": second.json()["reply"], "metadata": second.json()["metadata"]},
    ]
    assert provider.calls[-1]["messages"] == [
        {"role": "system", "content": "Answer briefly."},
        *[{key: row[key] for key in ("role", "content")} for row in history["messages"][:-1]],
    ]
    assert len(provider.calls[1]["messages"]) == 2


def test_unknown_session(client):
    response = client.get("/sessions/unknown/messages")
    assert (response.status_code, response.json()) == (404, {"detail": "session not found"})


def test_failed_turn_changes_neither_history_nor_prompt(client, provider):
    send(client, system_prompt="Give one sentence.")
    before = client.get("/sessions/first/messages").json()
    assert simulate(client, "*=429").status_code == 503
    rejected = client.post(
        "/chat", json={"session_id": "first", "message": "lost", "system_prompt": "Temporary."},
        headers={"X-Simulate-Failure": "*=429"},
    )
    assert rejected.status_code == 503
    assert client.get("/sessions/first/messages").json() == before
    send(client, message="another turn")
    assert provider.calls[-1]["messages"][0]["content"] == "Give one sentence."
    assert len(client.get("/sessions/first/messages").json()["messages"]) == 4


def test_restart_persists_history_and_settings(settings, provider):
    session = "id/with space"
    with TestClient(create_app(settings)) as first:
        reply = send(first, session, "Remember the light.", system_prompt="Use a lyrical voice.")
        assert reply.status_code == 200

    with TestClient(create_app(settings)) as restarted:
        history = restarted.get(f"/sessions/{quote(session, safe='')}/messages")
        assert history.status_code == 200
        assert history.json()["messages"][-1]["metadata"] == reply.json()["metadata"]
        assert send(restarted, session, "Describe it.").status_code == 200

    assert provider.calls[-1]["messages"][0]["content"] == "Use a lyrical voice."


def test_concurrent_turns_use_serialized_context(client, provider):
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda text: send(client, message=text), ["one", "two"]))
    assert [result.status_code for result in results] == [200, 200]
    assert [len(call["messages"]) for call in provider.calls] == [2, 4]
    history = client.get("/sessions/first/messages").json()["messages"]
    assert [row["role"] for row in history] == ["user", "assistant", "user", "assistant"]


def test_database_error_rolls_back_first_turn(client):
    with client.app.state.database.connect() as connection:
        connection.execute(
            """CREATE TRIGGER fail_assistant_insert BEFORE INSERT ON messages
               WHEN NEW.role = 'assistant'
               BEGIN SELECT RAISE(ABORT, 'assistant write failed'); END"""
        )

    failed = send(client)
    assert (failed.status_code, failed.json()) == (500, {"detail": "internal server error"})
    assert client.get("/sessions/first/messages").status_code == 404
    with client.app.state.database.connect() as connection:
        assert connection.execute("SELECT count(*) FROM messages").fetchone()[0] == 0
