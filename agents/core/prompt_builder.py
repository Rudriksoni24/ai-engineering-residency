from agents.tools.base import AgentTool


class AgentPromptBuilder:

    def build(
        self,
        user_query: str,
        tools: list[AgentTool],
    ) -> str:

        if not user_query.strip():
            raise ValueError(
                "user_query cannot be empty"
            )

        tool_lines = "\n".join(
            (
                f"- {tool.name}: "
                f"{tool.description}"
            )
            for tool in tools
        )

        return f"""You are a banking operations assistant.

Decide whether you can answer the user's request directly or whether you need to use one of the available tools.

Available tools:
{tool_lines}

Return exactly one JSON object.

If a tool is required:

{{
  "type": "tool",
  "tool_name": "<tool name>",
  "arguments": {{
    "<argument>": "<value>"
  }}
}}

If no tool is required:

{{
  "type": "final",
  "answer": "<final answer>"
}}

Rules:
1. Do not invent tool names.
2. Use a tool when the request requires information that only the tool can provide.
3. Do not wrap the JSON in markdown.
4. Return no text before or after the JSON.

User request:
{user_query}
"""