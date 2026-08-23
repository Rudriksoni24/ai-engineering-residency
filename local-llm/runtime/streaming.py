from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class StreamChunk:
    text: str
    done: bool = False


class StreamGenerationError(Exception):
    """Raised when streaming generation fails."""