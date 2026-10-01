# LLM Gateway

FastAPI gateway in front of OpenRouter.

## Structure

```
app/
  main.py            # FastAPI app, healthcheck
  api/v1/chat.py     # /v1 chat router
  core/config.py     # settings loaded from env / .env
  schemas/           # pydantic request/response models
  services/          # OpenRouter client and business logic
tests/               # pytest suite
.github/workflows/   # CI (ruff, pytest, docker build)
compose.yaml  Dockerfile  .env.example
```

## Configuration

```bash
cp .env.example .env   # then set OPENROUTER_API_KEY
```

## Run locally (Python 3.14 + [uv](https://docs.astral.sh/uv/))

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Check: `curl http://localhost:8000/healthcheck` (docs at `/docs`).

## Run with Docker Compose

```bash
docker compose up --build
```

Then open http://localhost:8000/healthcheck. Stop with `docker compose down`.

### Plain Docker

```bash
docker build -t llm-gateway .
docker run --rm -p 8000:8000 --env-file .env llm-gateway
```

`.env` is excluded from the image via `.dockerignore`; pass it at runtime.

## Lint and test

```bash
uv run ruff check .
uv run pytest
```

## License

MIT
