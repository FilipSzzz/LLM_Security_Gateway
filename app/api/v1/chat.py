from fastapi import APIRouter

from app.schemas.chat import ChatRequest

router = APIRouter(prefix="/v1")


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    return {"reply": "Chat endpoint is working!"}
