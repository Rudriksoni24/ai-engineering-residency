from fastapi import APIRouter, Depends

from api.contracts import (
    GenerateRequest,
    GenerateResponse,
)
from api.dependencies import get_llm_service
from api.services.llm_service import LLMService


router = APIRouter(
    prefix="/v1/generate",
    tags=["generation"],
)


@router.post(
    "",
    response_model=GenerateResponse,
)
def generate(
    request: GenerateRequest,
    service: LLMService = Depends(get_llm_service),
):
    response = service.generate(
        prompt=request.prompt,
        model=request.model,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
    )

    return GenerateResponse(
        text=response.text,
        model=response.model,
    )