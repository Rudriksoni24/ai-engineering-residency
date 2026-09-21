"""Dependency providers for the Local LLM API."""

import os
from functools import lru_cache

from local_llm.api.services.llm_service import LLMService
from local_llm.runtime.ollama_runtime import OllamaRuntime


@lru_cache
def get_llm_service() -> LLMService:
    """Return the configured LLM service."""

    base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434",
    )

    runtime = OllamaRuntime(
        base_url=base_url,
    )

    return LLMService(runtime)