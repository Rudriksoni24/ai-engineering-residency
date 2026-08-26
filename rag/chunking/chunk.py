from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Chunk:
    id: str
    content: str
    source: str
    index: int
    metadata: dict[str, Any] = field(
        default_factory=dict
    )