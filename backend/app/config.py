from dataclasses import dataclass, field
from os import getenv
from pathlib import Path


DEFAULT_SYSTEM_PROMPT = "You are Lantern, a helpful assistant. Give clear, accurate responses."


def csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    keys: tuple[str, ...] = field(repr=False)
    model: str = "gemini/gemini-2.5-flash"
    database_url: str = "sqlite:///./data/app.db"
    allowed_origins: tuple[str, ...] = ("http://localhost:3000",)
    enable_failure_simulation: bool = False
    provider_timeout: float = 18.0
    cache_ttl: int = 600
    api_base: str | None = None

    @property
    def database_path(self) -> Path:
        scheme = "sqlite:///"
        path = self.database_url.removeprefix(scheme)
        if not self.database_url.startswith(scheme) or path in ("", ":memory:"):
            raise ValueError("DATABASE_URL must point to a SQLite file")
        return Path(path).expanduser().resolve()

    @property
    def key_pool_ready(self) -> bool:
        return len(self.keys) >= 2 and len(set(self.keys)) == len(self.keys) and all(
            key and not key.startswith("replace_") for key in self.keys
        )

    @classmethod
    def from_env(cls) -> "Settings":
        from dotenv import load_dotenv

        # Existing process variables always win over the local .env file.
        load_dotenv()
        return cls(
            keys=csv(getenv("LLM_API_KEYS", "")),
            model=getenv("LLM_MODEL", cls.model).strip(),
            database_url=getenv("DATABASE_URL", cls.database_url),
            allowed_origins=csv(getenv("ALLOWED_ORIGINS", "http://localhost:3000")),
            enable_failure_simulation=getenv("ENABLE_FAILURE_SIMULATION", "").lower() == "true",
            provider_timeout=float(getenv("LLM_TIMEOUT_SECONDS", str(cls.provider_timeout))),
            cache_ttl=int(getenv("LLM_CACHE_TTL_SECONDS", str(cls.cache_ttl))),
            api_base=getenv("LLM_API_BASE") or None,
        )

    def __post_init__(self) -> None:
        if not self.model or not 0 < self.provider_timeout <= 120 or self.cache_ttl < 1:
            raise ValueError("Invalid model, provider timeout or cache TTL")
