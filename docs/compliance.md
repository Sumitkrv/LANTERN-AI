# Assignment compliance checklist

| Requirement from the Lyftr AI PDF | Implementation and verification path |
| --- | --- |
| Exactly three public API routes and JSON errors | `backend/app/api/routes`, `test_validation.py`, `test_health_and_usage.py` |
| Multi-turn conversation scoped to a client-generated session ID | `SessionService`, `SessionRepository`, `test_sessions.py` |
| Ordered history without the system prompt and with assistant metadata | SQLite repository and history endpoint, `test_sessions.py` |
| SQLite schema initialized on startup and durable storage | `Database`, Docker named volume, Render disk, restart test |
| LiteLLM with at least two configurable keys and deterministic retry | `LiteLLMGateway`, `test_failover.py`, live smoke test |
| Scoped `X-Simulate-Failure` with 429/500/502/503 and wildcard | Parser and gateway, `test_failover.py` |
| Clean 503, no partial DB writes | Chat route and transaction, provider and session tests |
| Built-in LiteLLM caching by model and entire context | `ResponseCache`, `test_cache.py`, live smoke test |
| Per-turn usage and measured latency, exact source/key metadata | Gateway, chat service, contract and smoke tests |
| Exact test IDs, fresh page sessions, readable errors, public-origin CORS | React components, `useChat`, CORS test, browser verification |
| Multi-stage Dockerfiles, SQLite volume and `make up` | Dockerfiles, `docker-compose.yml`, `Makefile` |
| Public frontend and backend, public GitHub source | Hosted deployment checklist and tracked `render.yaml`. Requires provider secrets and authorized hosting. |
| Two- to three-minute demo video with narration | Prepared [recording script](demo.md). Record from the verified public deployment. |

## Architecture

```text
React conversation → FastAPI contract → Session service → SQLite history
                                           │
                                           └→ LiteLLM cache or ordered provider calls
                                                   │
                                       SQLite transaction ← reply + usage
```

Cache identity, simulation cache bypass, provider usage, and atomic history writes are individually tested because failures in these areas can appear to work during a single ordinary chat turn.
