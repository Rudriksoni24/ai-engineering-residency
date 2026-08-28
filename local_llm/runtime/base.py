from abc import ABC, abstractmethod
from collections.abc import Iterator

from local_llm.runtime.runtime_types import (
    GenerationRequest,
    GenerationResponse,
)
from local_llm.runtime.streaming import StreamChunk


class LLMRuntime(ABC):

    @abstractmethod
    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        raise NotImplementedError

    @abstractmethod
    def generate_stream(
        self,
        request: GenerationRequest,
    ) -> Iterator[StreamChunk]:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        raise NotImplementedError