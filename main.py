from fastapi import FastAPI

app = FastAPI()


@app.get("/healthcheck")
def health():
    return {"status": "ok"}


def main():
    print("Hello from llm-gateway!")


if __name__ == "__main__":
    main()
