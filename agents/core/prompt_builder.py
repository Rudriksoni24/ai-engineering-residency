from __future__ import annotations

import json
from collections.abc import Sequence

from agents.contracts.agent import AgentStep
from agents.tools.registry import AgentToolRegistry


class AgentPromptBuilder:
    def build(
        self,
        user_query: str,
        registry: AgentToolRegistry,
        steps: Sequence[AgentStep] = (),
    ) -> str:
        if not user_query.strip():
            raise ValueError("user_query must not be empty")

        tools = [
            {
                "name": definition.name,
                "description": definition.description,
                "parameters": [
                    {
                        "name": parameter.name,
                        "type": parameter.parameter_type,
                        "description": parameter.description,
                        "required": parameter.required,
                    }
                    for parameter in definition.parameters
                ],
            }
            for definition in registry.definitions()
        ]

        trajectory = [
            {
                "iteration": step.iteration,
                "action": {
                    "tool_name": step.tool_name,
                    "arguments": step.arguments,
                },
                "observation": step.observation,
            }
            for step in steps
        ]

        return (
            "You are a tool-using agent.\n"
            "\n"
            "Complete the user's goal using the available tools when needed.\n"
            "You may make exactly one decision per response.\n"
            "\n"
            "Return exactly one JSON object and no other text.\n"
            "\n"
            "To request a tool:\n"
            '{\n'
            '  "type": "tool",\n'
            '  "tool_name": "<tool name>",\n'
            '  "arguments": {}\n'
            '}\n'
            "\n"
            "To provide the final answer:\n"
            '{\n'
            '  "type": "final",\n'
            '  "answer": "<answer>"\n'
            '}\n'
            "\n"
            "Do not include hidden reasoning, chain-of-thought, or a rationale.\n"
            "Use previous observations to decide the next action or final answer.\n"
            "Do not invent tool observations.\n"
            "\n"
            f"Available tools:\n{json.dumps(tools, indent=2, sort_keys=True)}\n"
            "\n"
            f"User goal:\n{user_query}\n"
            "\n"
            "Previous action/observation trajectory:\n"
            f"{json.dumps(trajectory, indent=2, sort_keys=True)}\n"
        )