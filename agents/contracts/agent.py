from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol


@dataclass(frozen=True)
class ToolCall:
    tool_name: str
    arguments: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.tool_name.strip():
            raise ValueError(
                "tool_name cannot be empty"
            )


@dataclass(frozen=True)
class AgentDecision:
    decision_type: Literal[
        "tool",
        "final",
    ]
    tool_call: ToolCall | None = None
    final_answer: str | None = None

    def __post_init__(self) -> None:
        if self.decision_type == "tool":
            if self.tool_call is None:
                raise ValueError(
                    "tool decision requires tool_call"
                )

            if self.final_answer is not None:
                raise ValueError(
                    "tool decision cannot contain final_answer"
                )

        if self.decision_type == "final":
            if not self.final_answer:
                raise ValueError(
                    "final decision requires final_answer"
                )

            if self.tool_call is not None:
                raise ValueError(
                    "final decision cannot contain tool_call"
                )
@dataclass(frozen=True)
class AgentStep:
    iteration: int
    tool_name: str
    arguments: dict[str, Any]
    observation: str

@dataclass(frozen=True)
class AgentResponse:
    answer: str
    tool_used: bool = False
    observation: str | None = None
    steps: tuple[AgentStep, ...] = field(default_factory=tuple)

class AgentGenerator(Protocol):
    def generate(self, prompt: str) -> str:
        ...