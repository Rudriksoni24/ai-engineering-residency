import json

from agents.tools.registry import (
    AgentToolRegistry,
)


class AgentPromptBuilder:

    def build(
        self,
        user_query: str,
        registry: AgentToolRegistry,
    ) -> str:

        if not user_query.strip():
            raise ValueError(
                "user_query cannot be empty"
            )

        tool_definitions = [
            {
                "name": definition.name,
                "description": (
                    definition.description
                ),
                "parameters": [
                    {
                        "name": parameter.name,
                        "type": (
                            parameter
                            .parameter_type
                        ),
                        "description": (
                            parameter
                            .description
                        ),
                        "required": (
                            parameter.required
                        ),
                    }
                    for parameter
                    in definition.parameters
                ],
            }
            for definition
            in registry.definitions()
        ]

        tools_json = json.dumps(
            tool_definitions,
            indent=2,
        )

        return f"""You are a banking operations assistant.

Decide whether the user's request can be answered directly or requires one of the available tools.

Available tools:
{tools_json}

Return exactly one JSON object.

Tool request:

{{
  "type": "tool",
  "tool_name": "<registered tool name>",
  "arguments": {{
    "<argument name>": "<value>"
  }}
}}

Direct answer:

{{
  "type": "final",
  "answer": "<final answer>"
}}

Rules:
1. Use only registered tools.
2. Follow the tool argument definitions exactly.
3. Do not invent arguments.
4. Use a tool when external banking information is required.
5. Do not wrap the result in markdown.
6. Return no text before or after the JSON.

User request:
{user_query}
"""