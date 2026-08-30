from dataclasses import dataclass
from typing import Literal

MemoryRole = Literal[
    "user",
    "assistant",
]


@dataclass(frozen=True)
class MemoryMessage:
    role: MemoryRole
    content: str