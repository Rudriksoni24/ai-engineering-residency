from typing import Any
from local_llm.runtime.base import LLMRuntime
from local_llm.runtime.runtime_types import GenerationRequest


class LocalGenerator:
    """RAG generation manager that delegates inference tasks to the Sprint 2 LLM runtime framework."""

    def __init__(
        self,
        llm_client: LLMRuntime,
        default_model: str = "qwen2.5:3b",
        default_max_tokens: int = 512,
        default_temperature: float = 0.3,
    ) -> None:
        """Initializes the generator with a decoupled runtime client dependency."""
        self.llm_client = llm_client
        self.default_model = default_model
        self.default_max_tokens = default_max_tokens
        self.default_temperature = default_temperature

    def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """Wraps the incoming prompt inside our standard runtime GenerationRequest object.
        
        Allows overriding request options dynamically via kwargs (e.g. temperature, max_tokens).
        """
        # Build the exact contract payload our runtime engine expects
        request = GenerationRequest(
            prompt=prompt,
            model=kwargs.get("model", self.default_model),
            max_tokens=kwargs.get("max_tokens", self.default_max_tokens),
            temperature=kwargs.get("temperature", self.default_temperature),
            top_p=kwargs.get("top_p"),
            seed=kwargs.get("seed"),
        )

        # Execute via our unified interface boundary
        response = self.llm_client.generate(request)
        
        return response.text
