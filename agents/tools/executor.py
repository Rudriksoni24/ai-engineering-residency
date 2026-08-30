from typing import Any

from agents.tools.contracts import (
    ToolDefinition,
    ToolParameter,
    ToolResult,
)
from agents.tools.registry import (
    AgentToolRegistry,
)


class AgentToolExecutor:

    def __init__(
        self,
        registry: AgentToolRegistry,
    ) -> None:
        self.registry = registry

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> ToolResult:

        tool = self.registry.get(
            tool_name
        )

        if tool is None:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                observation="",
                error=(
                    "unknown tool requested: "
                    f"{tool_name}"
                ),
            )

        validation_error = (
            self._validate_arguments(
                definition=tool.definition,
                arguments=arguments,
            )
        )

        if validation_error is not None:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                observation="",
                error=validation_error,
            )

        try:
            observation = tool.execute(
                arguments
            )
        except Exception as exc:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                observation="",
                error=str(exc),
            )

        return ToolResult(
            tool_name=tool_name,
            success=True,
            observation=observation,
            error=None,
        )

    @classmethod
    def _validate_arguments(
        cls,
        definition: ToolDefinition,
        arguments: dict[str, Any],
    ) -> str | None:

        if not isinstance(
            arguments,
            dict,
        ):
            return (
                "tool arguments must "
                "be an object"
            )

        declared_names = {
            parameter.name
            for parameter
            in definition.parameters
        }

        unknown_arguments = (
            set(arguments)
            - declared_names
        )

        if unknown_arguments:
            names = ", ".join(
                sorted(
                    unknown_arguments
                )
            )

            return (
                "unknown tool arguments: "
                f"{names}"
            )

        for parameter in (
            definition.parameters
        ):
            error = cls._validate_parameter(
                parameter,
                arguments,
            )

            if error is not None:
                return error

        return None

    @staticmethod
    def _validate_parameter(
        parameter: ToolParameter,
        arguments: dict[str, Any],
    ) -> str | None:

        if parameter.name not in arguments:

            if parameter.required:
                return (
                    "missing required "
                    "argument: "
                    f"{parameter.name}"
                )

            return None

        value = arguments[
            parameter.name
        ]

        if (
            parameter.parameter_type
            == "string"
        ):
            if not isinstance(
                value,
                str,
            ) or not value.strip():
                return (
                    "argument "
                    f"{parameter.name} "
                    "must be a non-empty string"
                )

            return None

        if (
            parameter.parameter_type
            == "integer"
        ):
            if (
                not isinstance(
                    value,
                    int,
                )
                or isinstance(
                    value,
                    bool,
                )
            ):
                return (
                    "argument "
                    f"{parameter.name} "
                    "must be an integer"
                )

            return None

        if (
            parameter.parameter_type
            == "number"
        ):
            if (
                not isinstance(
                    value,
                    (int, float),
                )
                or isinstance(
                    value,
                    bool,
                )
            ):
                return (
                    "argument "
                    f"{parameter.name} "
                    "must be a number"
                )

            return None

        if (
            parameter.parameter_type
            == "boolean"
        ):
            if not isinstance(
                value,
                bool,
            ):
                return (
                    "argument "
                    f"{parameter.name} "
                    "must be a boolean"
                )

            return None

        return (
            "unsupported parameter type: "
            f"{parameter.parameter_type}"
        )