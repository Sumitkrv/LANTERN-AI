import logging
import os
from contextlib import asynccontextmanager
from time import perf_counter

# Disable third-party diagnostics before importing the SDK.
os.environ.setdefault("LITELLM_LOG", "CRITICAL")
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("LITELLM_TELEMETRY", "False")

import litellm
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from app.api.routes import chat, health, sessions
from app.config import Settings
from app.database import Database
from app.repositories.sessions import SessionRepository
from app.services.chat import ChatService
from app.services.litellm_gateway import LiteLLMGateway
from app.services.sessions import SessionService


logger = logging.getLogger("lantern")


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        litellm.telemetry = False
        litellm.turn_off_message_logging = True
        database = Database(config.database_path)
        await run_in_threadpool(database.initialize)
        session_service = SessionService(SessionRepository(database))
        app.state.settings = config
        app.state.database = database
        app.state.sessions = session_service
        app.state.chat = ChatService(session_service, LiteLLMGateway(config))
        yield

    app = FastAPI(
        title="LANTERN AI", lifespan=lifespan, openapi_url=None, docs_url=None,
        redoc_url=None, redirect_slashes=False,
    )

    @app.middleware("http")
    async def safe_errors(request: Request, call_next):
        request.state.started_at = perf_counter()
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error("Request failed internally type=%s", type(exc).__name__)
            return JSONResponse({"detail": "internal server error"}, status_code=500)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, exc: RequestValidationError):
        detail = [
            {key: error[key] for key in ("loc", "msg", "type")}
            for error in exc.errors()
        ]
        return JSONResponse({"detail": detail}, status_code=422)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.allowed_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Simulate-Failure"],
    )
    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(sessions.router)
    return app


app = create_app()
