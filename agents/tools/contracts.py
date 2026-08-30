from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolParameter:
    name: str
    parameter_type: str
    description: str
    required: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError(
                "parameter name cannot be empty"
            )

        if not self.parameter_type.strip():
            raise ValueError(
                "parameter_type cannot be empty"
            )


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: list[ToolParameter] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError(
                "tool name cannot be empty"
            )

        if not self.description.strip():
            raise ValueError(
                "tool description cannot be empty"
            )


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    success: bool
    observation: str
    error: str | None = None