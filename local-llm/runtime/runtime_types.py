from dataclasses import dataclass, field
from typing import Any


@dataclass
class GenerationRequest:
    """Represents the configuration payload sent to a local LLM runner."""
    prompt: str
    model: str
    max_tokens: int = 256
    temperature: float = 0.7


@dataclass
class GenerationResponse:
    """Encapsulates the standard response output from a local LLM execution."""
    text: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
