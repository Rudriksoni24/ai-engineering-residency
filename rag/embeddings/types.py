from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EmbeddedChunk:
    chunk_id: str
    content: str
    source: str
    index: int
    embedding: list[float]
    model: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )