import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

UPSTREAM_OK = {"choices": [{"message": {"content": "Hello!"}}], "provider": "x", "usage": {}}


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@respx.mock
def test_chat_returns_only_the_reply(client):
    route = respx.post(settings.openrouter_url).respond(200, json=UPSTREAM_OK)
    response = client.post("/v1/chat", json={"prompt": "hi"})
    assert response.status_code == 200
    assert response.json() == {"reply": "Hello!"}
    assert route.calls.last.request.headers["Authorization"] == "Bearer test-key"


@respx.mock
def test_empty_prompt_never_reaches_upstream(client):
    route = respx.post(settings.openrouter_url)
    response = client.post("/v1/chat", json={"prompt": ""})
    assert response.status_code == 422
    assert not route.called


@respx.mock
@pytest.mark.parametrize(
    ("upstream", "expected"),
    [
        (httpx.ReadTimeout("slow"), 504),
        (httpx.ConnectError("dns"), 502),
        (httpx.Response(401), 502),
        (httpx.Response(500), 502),
        (httpx.Response(200, json={"error": "weird"}), 502),
    ],
)
def test_upstream_errors_map_to_status(client, upstream, expected):
    respx.post(settings.openrouter_url).mock(side_effect=[upstream])
    assert client.post("/v1/chat", json={"prompt": "hi"}).status_code == expected


@respx.mock
def test_upstream_429_passes_retry_after(client):
    respx.post(settings.openrouter_url).respond(429, headers={"Retry-After": "30"})
    response = client.post("/v1/chat", json={"prompt": "hi"})
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "30"


def test_bad_request_id_is_replaced(client):
    response = client.get("/healthcheck", headers={"X-Request-ID": "x" * 500})
    assert len(response.headers["X-Request-ID"]) == 32
