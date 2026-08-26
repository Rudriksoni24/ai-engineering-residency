from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VectorRecord:
    id: str
    embedding: list[float]
    content: str
    source: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class RetrievalResult:
    id: str
    content: str
    source: str
    score: float
    metadata: dict[str, Any]