from fastapi import FastAPI

app = FastAPI()


@app.get("/healthcheck")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    pass
