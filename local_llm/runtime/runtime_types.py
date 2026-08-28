from dataclasses import dataclass
from typing import Any


@dataclass
class GenerationRequest:
    prompt: str
    model: str
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float | None = None
    seed: int | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class GenerationResponse:
    text: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    metadata: dict[str, Any] | None = None