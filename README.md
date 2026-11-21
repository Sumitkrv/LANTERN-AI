# LANTERN AI

**Intelligence that stays connected.**

LANTERN AI is a multi-turn chat workspace with a per-reply inspector that shows the selected answer’s source, model, server latency, token usage, and path through the provider key pool. The frontend uses React, TypeScript and Vite. The Python API uses FastAPI, LiteLLM and SQLite.

## Live URLs

| Service | Local | Public |
| --- | --- | --- |
| Frontend | http://localhost:3000 | Requires the deployed API URL |
| Backend | http://localhost:8000/health | Requires a host with a persistent disk and two provider keys |
| Source | This checkout | [LANTERN-AI on GitHub](https://github.com/Sumitkrv/LANTERN-AI) |

The [demo script](docs/demo.md) covers the two to three minute submission recording.

## Run locally: with Docker and without

### With Docker

Requirements are Docker with Compose, Make, and two distinct API keys for a single LiteLLM-compatible model.

```sh
cp .env.example .env
# Edit .env and fill in LLM_API_KEYS and LLM_MODEL for your provider.
make up
curl -fsS http://localhost:8000/health
```

Open http://localhost:3000. The API listens on port 8000. Use `make logs` to follow startup and `make down` to stop the stack. The `lantern_data` volume keeps session history through container replacement and restarts. If port 8000 is taken, set `BACKEND_HOST_PORT` and point `VITE_API_BASE_URL` at the new host port before running `make up`. When source or the frontend API URL changes, run `docker compose build` before restarting.

### Without Docker

Use Python 3.12 and Node.js 22.13 or later. In the root `.env`, set `DATABASE_URL=sqlite:///./data/app.db` and configure both keys.

```sh
cd backend
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --port 8000 --workers 1 --no-access-log
```

In a second terminal at the repository root:

```sh
cd frontend
npm ci
npm run dev
```

### Environment variables

| Variable | Purpose |
| --- | --- |
| `LLM_API_KEYS` | Comma-separated list of at least two distinct secrets that can call the configured model. |
| `LLM_MODEL` | LiteLLM model identifier. The example uses `gemini/gemini-3.5-flash-lite`. |
| `LLM_API_BASE` | Optional provider API base, such as an OpenAI-compatible server's `/v1` base. Leave blank for Gemini or the provider's default. |
| `LLM_TIMEOUT_SECONDS` | Per-key inference timeout. Defaults to 18 seconds. |
| `LLM_CACHE_TTL_SECONDS` | Process-local cache lifetime. Defaults to 600 seconds. |
| `DATABASE_URL` | SQLite file URL. Docker and hosted deployment use `sqlite:////data/app.db`. |
| `ALLOWED_ORIGINS` | Comma-separated browser origins, including scheme and any port. |
| `ENABLE_FAILURE_SIMULATION` | Enables the `X-Simulate-Failure` hook when set to `true`. |
| `VITE_API_BASE_URL` | Browser-facing backend base URL, embedded into the frontend at build time. |
| `PORT` | Backend Docker port, normally 8000 locally or injected by the host. |
| `BACKEND_HOST_PORT` | Compose host port for the backend. Defaults to 8000. |

### Public deployment

1. Push this checkout to the public GitHub repository.
2. Import `render.yaml` as a Render Blueprint. It provisions a Docker web service with a persistent disk mounted at `/data` and a static frontend build. The persistent disk requires a paid backend plan.
3. Set `LLM_API_KEYS` in the backend host's secret configuration and choose `LLM_MODEL`. Keep the backend at one worker and one instance. Set `ALLOWED_ORIGINS` to the actual public frontend origin. The blueprint enables the failure simulation hook for evaluation.
4. Set the frontend's `VITE_API_BASE_URL` to the public backend base and build again. A Vercel or Netlify static deployment is also supported using `frontend` as the project root, `npm run build`, and `dist` as the output directory.
5. Run `python scripts/smoke.py https://YOUR-BACKEND` and open the frontend in a fresh browser. Add both verified public URLs above, update the demo with those URLs, and record the submission.

The Docker entrypoint sets the mounted `/data` owner and then runs the API as UID/GID `10001`. A `503` from `/health` can indicate missing keys or a database that the service cannot read. A browser connection error with a working API usually calls for checking `ALLOWED_ORIGINS` and rebuilding with the correct `VITE_API_BASE_URL`. During provider troubleshooting, use two real keys for the same model, ideally with independent quotas.

## Design decisions: key fallback, caching, SQLite session storage

- **Key fallback.** The gateway calls LiteLLM’s asynchronous completion interface once per configured key in order. Rate limiting, quota errors, provider 5xx, transport failures, and invalid credentials can advance the sequence. Attempts have individual timeouts, and SDK retries are disabled. A failed key is eligible again in the next request.
- **Caching.** The gateway reads and writes through LiteLLM's built-in in-memory `Cache`. A SHA-256 key covers the model and full ordered provider message list. Session IDs and credentials are excluded. Only validated reply text and the provider's two usage counts are cached. A cache hit is identified by a successful cache lookup. Enabled simulation skips lookup and storage so it can exercise every configured key.
- **SQLite session storage.** The server builds context from the session's system prompt and ordered SQLite messages. A single transaction updates the prompt and inserts the user and assistant pair. Same-session turns serialize within the single worker so concurrent requests see complete conversation history. Different sessions can call providers concurrently. The history route reads a consistent SQLite snapshot. WAL lets reads proceed while turns commit.
- **Metadata.** Live token counts come from LiteLLM's normalized provider usage. Cache hits preserve those counts and measure a fresh latency. Timing uses a monotonic clock from HTTP entry through completion of inference or cache lookup. The reply inspector derives its route from those values.
- **Errors.** Invalid requests return 422, unknown sessions return 404, and exhausted key pools return 503. Error responses have a JSON `detail` field. Provider logs record the key identifier and exception type. The UI keeps the draft available to retry.

```text
frontend/src/          Conversation UI, API client, response inspector
backend/app/api/       Three HTTP routes
backend/app/services/  Context assembly, LiteLLM gateway and response cache
backend/app/repositories/
                       Transactional SQLite access
backend/tests/         API contract, cache, persistence and failover tests
scripts/smoke.py       Verification against a running API and real inference
render.yaml            Public web services and durable SQLite disk
```

## Verification: how to see failover, cache hits and per-message token usage

```sh
make test                  # Activate backend/.venv first for a local install
make build
```

The automated tests replace the provider boundary while exercising the real FastAPI routes, SQLite repository and LiteLLM cache. The smoke test issues actual calls against the running backend and incurs normal provider usage.

Run these examples in order with two keys and simulation enabled. Replace the example base URL when checking a public deployment.

```sh
API=http://localhost:8000
RUN=$(date +%s)
FIRST="demo-${RUN}-first"
SECOND="demo-${RUN}-second"
PROMPT="My favorite fruit is a pear. Confirm in one sentence. Reference ${RUN}."

curl -fsS "$API/health"

# First request uses live inference in this run.
curl -fsS "$API/chat" -H 'Content-Type: application/json' \
  --data "{\"session_id\":\"$FIRST\",\"message\":\"$PROMPT\"}"

# Identical first turn in a new session uses LLM_CACHE with identical usage and reply.
curl -fsS "$API/chat" -H 'Content-Type: application/json' \
  --data "{\"session_id\":\"$SECOND\",\"message\":\"$PROMPT\"}"

# The backend recalls the earlier message. Input usage includes the preceding turn.
curl -fsS "$API/chat" -H 'Content-Type: application/json' \
  --data "{\"session_id\":\"$FIRST\",\"message\":\"What is my favorite fruit? Answer in one word.\"}"

curl -fsS "$API/sessions/$FIRST/messages"

# Simulation bypasses the existing cache entry. Expect LIVE_INFERENCE and key_2.
curl -fsS "$API/chat" -H 'Content-Type: application/json' \
  -H 'X-Simulate-Failure: key_1=429' \
  --data "{\"session_id\":\"demo-$RUN-fallback\",\"message\":\"$PROMPT\"}"

# Expect HTTP 503, then retrieve the unchanged original history again.
curl -sS -i "$API/chat" -H 'Content-Type: application/json' \
  -H 'X-Simulate-Failure: *=429' \
  --data "{\"session_id\":\"$FIRST\",\"message\":\"This turn should never be stored.\"}"
curl -fsS "$API/sessions/$FIRST/messages"

# Automated live API checks.
python scripts/smoke.py "$API"
```

In the browser, send a first prompt, select **New conversation**, and send the exact same first prompt with the same session settings before the cache expires. Compare the reply labels and token counts, then select a reply’s waveform button to inspect its full route. To confirm persistence with Docker, record a session ID from your API request, run `docker compose restart backend`, and request the same history again.

## Setup Used: your editor and AI tools

Codex in the managed Linux workspace was used to implement and test the project, along with ImageGen for the welcome illustration. Verification uses Pytest, npm/Vite, Docker Compose, Chromium, and a local Qwen model served by llama.cpp for genuine inference.

## Bonus features (if any): what you added beyond the requirements and why

- A response inspector shows the exact key route or cache path for a selected reply. The same data remains available per reply, including on mobile.
- Session settings let users set a system prompt. The backend remembers the prompt with the active conversation.
- Assistant replies support sanitized Markdown, tables, code and one-click copying.
