import json
from collections.abc import Sequence

from agents.contracts.agent import AgentStep
from agents.memory.contracts import MemoryMessage
from agents.tools.registry import AgentToolRegistry


class AgentPromptBuilder:
    def build(
        self,
        *,
        user_query: str,
        registry: AgentToolRegistry,
        steps: Sequence[AgentStep] = (),
        memory: Sequence[MemoryMessage] = (),
    ) -> str:
        normalized_query = user_query.strip()

        if not normalized_query:
            raise ValueError(
                "user_query cannot be empty"
            )

        tools = [
            {
                "name": definition.name,
                "description": (
                    definition.description
                ),
                "parameters": [
                    {
                        "name": parameter.name,
                        "type": (
                            parameter.parameter_type
                        ),
                        "description": (
                            parameter.description
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

        memory_payload = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in memory
        ]

        trajectory = [
            {
                "iteration": step.iteration,
                "action": {
                    "tool_name": (
                        step.tool_name
                    ),
                    "arguments": (
                        step.arguments
                    ),
                },
                "observation": (
                    step.observation
                ),
            }
            for step in steps
        ]

        return f"""
You are a tool-using agent.

You may either:

1. call exactly one available tool
2. return a final answer

Return exactly one JSON object.

The "type" field may contain ONLY one of these values:

- "tool"
- "final"

Never use values such as:
- "tool_decision"
- "final_answer"

Tool decision format:

{{
  "type": "tool",
  "tool_name": "tool_name",
  "arguments": {{
    "argument": "value"
  }}
}}

Final decision format:

{{
  "type": "final",
  "answer": "answer"
}}

Available tools:

{json.dumps(
    tools,
    indent=2,
)}

Conversation memory from earlier completed turns:

{json.dumps(
    memory_payload,
    indent=2,
)}

Current execution trajectory:

{json.dumps(
    trajectory,
    indent=2,
)}

Current user query:

{normalized_query}

Use conversation memory only when relevant to the current query.

Tool observations in the current execution trajectory are authoritative
for the current run.

Do not invent tool results.

Do not expose hidden reasoning, chain-of-thought, or private rationale.

If a tool is needed, return a tool decision.

If enough information is available to answer, return a final decision.

Do not infer facts that require another available tool lookup.

If an observation contains an identifier for another entity needed to answer
the user's question, call the appropriate tool before producing a final answer.

For example, if a transaction observation contains an account_id and the user
asks who owns that account, you must call the account lookup tool before
answering.

A tool observation is evidence only for the fields explicitly present in that
observation.
""".strip()