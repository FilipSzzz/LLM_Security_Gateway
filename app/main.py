from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.v1.chat import router as chat_router

load_dotenv()

app = FastAPI()
app.include_router(chat_router)

@app.get("/healthcheck")
def health():
    return {"status": "ok"}

def main():
    print("Hello from llm-gateway!")

if __name__ == "__main__":
    main()
