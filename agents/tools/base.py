from typing import Any, Protocol


class AgentTool(Protocol):

    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:
        ...