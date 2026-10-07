import logging

import httpx
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


async def complete(client: httpx.AsyncClient, prompt: str) -> str:
    try:
        response = await client.post(
            settings.openrouter_url,
            headers={"Authorization": f"Bearer {settings.openrouter_api_key.get_secret_value()}"},
            json={
                "model": settings.default_model,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
    except httpx.TimeoutException as exc:
        logger.warning("upstream timeout: %s", type(exc).__name__)
        raise HTTPException(504, "Upstream timed out") from exc
    except httpx.RequestError as exc:
        logger.warning("upstream unreachable: %s", type(exc).__name__)
        raise HTTPException(502, "Upstream unreachable") from exc

    if response.status_code == 429:
        headers = {}
        if retry_after := response.headers.get("Retry-After"):
            headers["Retry-After"] = retry_after
        raise HTTPException(429, "Upstream rate limit reached", headers=headers)
    if response.status_code != 200:
        logger.error("upstream returned %d", response.status_code)
        raise HTTPException(502, "Upstream error")

    try:
        return response.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        logger.error("upstream returned an unexpected body")
        raise HTTPException(502, "Upstream returned an invalid response") from exc
