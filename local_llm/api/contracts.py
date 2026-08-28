from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=20_000,
    )

    model: str = "qwen2.5:3b"

    max_tokens: int = Field(
        default=256,
        ge=1,
        le=4096,
    )

    temperature: float = Field(
        default=0.7,
        ge=0,
        le=2,
    )


class GenerateResponse(BaseModel):
    text: str
    model: str