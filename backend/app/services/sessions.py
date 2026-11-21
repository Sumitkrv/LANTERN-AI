import asyncio
from weakref import WeakValueDictionary

from starlette.concurrency import run_in_threadpool

from app.config import DEFAULT_SYSTEM_PROMPT
from app.repositories.sessions import SessionRepository
from app.schemas import ChatRequest, SessionMessages


class SessionService:
    def __init__(self, repository: SessionRepository) -> None:
        self.repository = repository
        self._locks: WeakValueDictionary[str, asyncio.Lock] = WeakValueDictionary()

    def lock(self, session_id: str) -> asyncio.Lock:
        # The single event loop owns this registry. Active turns keep their lock alive.
        lock = self._locks.get(session_id)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[session_id] = lock
        return lock

    async def history(self, session_id: str) -> SessionMessages | None:
        stored = await run_in_threadpool(self.repository.read, session_id)
        if stored is None:
            return None
        return SessionMessages(session_id=session_id, messages=stored.messages)

    async def prepare(self, request: ChatRequest) -> tuple[str, list[dict[str, str]]]:
        stored = await run_in_threadpool(self.repository.read, request.session_id)
        system_prompt = request.system_prompt
        if system_prompt is None:
            system_prompt = stored.system_prompt if stored else DEFAULT_SYSTEM_PROMPT

        messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
        if stored:
            messages.extend({"role": item.role, "content": item.content} for item in stored.messages)
        messages.append({"role": "user", "content": request.message})
        return system_prompt, messages
