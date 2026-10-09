from fastapi import APIRouter, Request

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.detector import detector_check
from app.services.upstream import complete

router = APIRouter(prefix="/v1")


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest, request: Request):
    detector_check(body.prompt)
    reply = await complete(request.app.state.http_client, body.prompt)
    return {"reply": reply}
