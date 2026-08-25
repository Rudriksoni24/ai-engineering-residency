from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_llm_service
from api.services.llm_service import LLMService


router = APIRouter(
    tags=["health"],
)


@router.get("/health")
def health():
    return {
        "status": "ok",
    }


@router.get("/ready")
def ready(
    service: LLMService = Depends(get_llm_service),
):
    if not service.runtime.health_check():
        raise HTTPException(
            status_code=503,
            detail="LLM runtime unavailable",
        )

    return {
        "status": "ready",
    }