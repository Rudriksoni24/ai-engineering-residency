from agents.tools.base import AgentTool
from agents.tools.contracts import (
    ToolDefinition,
)


class AgentToolRegistry:

    def __init__(
        self,
        tools: list[AgentTool] | None = None,
    ) -> None:

        self._tools: dict[
            str,
            AgentTool,
        ] = {}

        for tool in tools or []:
            self.register(tool)

    def register(
        self,
        tool: AgentTool,
    ) -> None:

        name = tool.definition.name

        if name in self._tools:
            raise ValueError(
                f"tool already registered: {name}"
            )

        self._tools[name] = tool

    def get(
        self,
        name: str,
    ) -> AgentTool | None:

        return self._tools.get(name)

    def require(
        self,
        name: str,
    ) -> AgentTool:

        tool = self.get(name)

        if tool is None:
            raise ValueError(
                f"unknown tool requested: {name}"
            )

        return tool

    def definitions(
        self,
    ) -> list[ToolDefinition]:

        return sorted(
            (
                tool.definition
                for tool
                in self._tools.values()
            ),
            key=lambda definition: (
                definition.name
            ),
        )

    def names(
        self,
    ) -> list[str]:

        return [
            definition.name
            for definition
            in self.definitions()
        ]

    def __len__(
        self,
    ) -> int:
        return len(self._tools)