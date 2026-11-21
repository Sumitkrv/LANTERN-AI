from dataclasses import dataclass
from datetime import datetime, timezone

from app.database import Database
from app.schemas import AssistantMessage, ResponseMetadata, UserMessage


@dataclass(frozen=True)
class StoredSession:
    system_prompt: str
    messages: list[UserMessage | AssistantMessage]


class SessionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def read(self, session_id: str) -> StoredSession | None:
        with self.database.connect() as connection:
            connection.execute("BEGIN")
            session = connection.execute(
                "SELECT system_prompt FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
            if session is None:
                return None
            rows = connection.execute(
                "SELECT role, content, metadata FROM messages WHERE session_id = ? ORDER BY id",
                (session_id,),
            ).fetchall()

        messages: list[UserMessage | AssistantMessage] = []
        for row in rows:
            if row["role"] == "assistant":
                metadata = ResponseMetadata.model_validate_json(row["metadata"])
                messages.append(AssistantMessage(content=row["content"], metadata=metadata))
            else:
                messages.append(UserMessage(content=row["content"]))
        return StoredSession(system_prompt=session["system_prompt"], messages=messages)

    def save_turn(
        self, session_id: str, system_prompt: str, message: str, reply: str,
        metadata: ResponseMetadata,
    ) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        with self.database.connect() as connection:
            connection.execute(
                """INSERT INTO sessions (id, system_prompt) VALUES (?, ?)
                   ON CONFLICT(id) DO UPDATE SET system_prompt = excluded.system_prompt""",
                (session_id, system_prompt),
            )
            connection.executemany(
                """INSERT INTO messages (session_id, role, content, metadata, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                [
                    (session_id, "user", message, None, timestamp),
                    (session_id, "assistant", reply, metadata.model_dump_json(), timestamp),
                ],
            )
