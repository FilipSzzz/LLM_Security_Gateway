import logging
import time
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, Request

from app.api.v1.chat import router as chat_router
from app.core.config import settings
from app.core.logging_config import request_id_var, setup_logging

load_dotenv()
setup_logging(settings.log_level, settings.log_json)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(chat_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
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
