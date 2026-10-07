import logging
import re
import time
import uuid
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request

from app.api.v1.chat import router as chat_router
from app.core.config import settings
from app.core.logging_config import request_id_var, setup_logging

setup_logging(settings.log_level, settings.log_json)
logger = logging.getLogger(__name__)

REQUEST_ID_RE = re.compile(r"[A-Za-z0-9-]{1,64}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan for the FastAPI app."""
    timeout = httpx.Timeout(
        settings.upstream_read_timeout, connect=settings.upstream_connect_timeout
    )
    async with httpx.AsyncClient(timeout=timeout) as client:
        app.state.http_client = client
        yield


app = FastAPI(lifespan=lifespan)
app.include_router(chat_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", "")
    if not REQUEST_ID_RE.fullmatch(request_id):
        request_id = uuid.uuid4().hex
    token = request_id_var.set(request_id)
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("%s %s failed", request.method, request.url.path)
        raise
    else:
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "%s %s -> %d (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            (time.perf_counter() - start) * 1000,
        )
        return response
    finally:
        request_id_var.reset(token)


@app.get("/healthcheck")
def health():
    return {"status": "ok"}
