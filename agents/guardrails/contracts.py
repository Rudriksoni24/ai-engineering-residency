from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentGuardrailConfig:
    max_final_answer_chars: int = 4000
    max_tool_arguments: int = 10

    blocked_tools: frozenset[str] = field(
        default_factory=frozenset
    )

    def __post_init__(self) -> None:
        if self.max_final_answer_chars <= 0:
            raise ValueError(
                "max_final_answer_chars must be "
                "greater than zero"
            )

        if self.max_tool_arguments < 0:
            raise ValueError(
                "max_tool_arguments cannot be negative"
            )