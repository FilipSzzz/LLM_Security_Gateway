from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(
        description="The prompt to forward to the model",
        min_length=1,
        max_length=8000,
    )
