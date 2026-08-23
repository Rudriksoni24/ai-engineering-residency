from abc import ABC, abstractmethod

from .runtime_types import GenerationRequest, GenerationResponse


class LLMRuntime(ABC):
    """Abstract interface defining standard operations for local LLM runtimes.
    
    Serves as the foundational boundary separating application logic from specific 
    backend engines (e.g., Ollama, Llama.cpp, Hugging Face).
    """

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate a text completion using the specified request parameters.

        Args:
            request: A GenerationRequest container holding prompts and sampling configs.

        Returns:
            A GenerationResponse object containing text and token metrics.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Verify if the backend local LLM engine is running and reachable.

        Returns:
            True if the engine is ready to process requests, False otherwise.
        """
        raise NotImplementedError
