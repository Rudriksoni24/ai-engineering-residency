from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentEvaluationCase:
    case_id: str
    user_query: str

    expected_success: bool = True

    required_answer_keywords: tuple[str, ...] = field(
        default_factory=tuple
    )

    expected_tools: tuple[str, ...] = field(
        default_factory=tuple
    )

    expected_tool_sequence: tuple[str, ...] | None = None

    max_steps: int | None = None

    expected_error_keywords: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError(
                "case_id cannot be empty"
            )

        if not self.user_query.strip():
            raise ValueError(
                "user_query cannot be empty"
            )

        if (
            self.max_steps is not None
            and self.max_steps < 0
        ):
            raise ValueError(
                "max_steps cannot be negative"
            )


@dataclass(frozen=True)
class AgentEvaluationResult:
    case_id: str
    passed: bool

    answer: str | None
    actual_tools: tuple[str, ...]
    step_count: int

    error: str | None

    checks: tuple[tuple[str, bool], ...]