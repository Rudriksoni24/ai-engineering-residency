from functools import lru_cache

from runtime.ollama_runtime import OllamaRuntime

from api.services.llm_service import LLMService


@lru_cache
def get_llm_service() -> LLMService:
    runtime = OllamaRuntime()

    return LLMService(runtime)