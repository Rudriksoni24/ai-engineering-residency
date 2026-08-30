from typing import Any, Protocol

from agents.tools.contracts import (
    ToolDefinition,
)


class AgentTool(Protocol):

    @property
    def definition(
        self,
    ) -> ToolDefinition:
        ...

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:
        ...