import logging

from fastapi import APIRouter, Request

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.detector import detector_check
from app.services.pii import mask_pii
from app.services.upstream import complete

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1")


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest, request: Request):
    detector_check(body.prompt)
    prompt, counts = mask_pii(body.prompt)
    if any(counts.values()):
        logger.info(
            "pii masked: card=%d pesel=%d email=%d",
            counts["card"],
            counts["pesel"],
            counts["email"],
        )
    reply = await complete(request.app.state.http_client, prompt)
    return {"reply": reply}
