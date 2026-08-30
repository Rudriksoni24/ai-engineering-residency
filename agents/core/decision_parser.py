import json
from typing import Any

from agents.contracts.agent import (
    AgentDecision,
    ToolCall,
)


class AgentDecisionParser:

    def parse(
        self,
        raw_response: str,
    ) -> AgentDecision:

        if not raw_response.strip():
            raise ValueError(
                "agent response cannot be empty"
            )

        try:
            payload: dict[str, Any] = (
                json.loads(raw_response)
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                "agent response is not valid JSON"
            ) from exc

        decision_type = payload.get(
            "type"
        )
        if decision_type not in {"tool", "final"}:
            raise ValueError(
                f"unsupported decision type: {decision_type}"
            )

        if decision_type == "final":

            answer = payload.get(
                "answer"
            )

            if not isinstance(
                answer,
                str,
            ) or not answer.strip():
                raise ValueError(
                    "final decision requires answer"
                )

            return AgentDecision(
                decision_type="final",
                final_answer=answer.strip(),
            )

        if decision_type == "tool":

            tool_name = payload.get(
                "tool_name"
            )

            arguments = payload.get(
                "arguments",
                {},
            )

            if not isinstance(
                tool_name,
                str,
            ) or not tool_name.strip():
                raise ValueError(
                    "tool decision requires tool_name"
                )

            if not isinstance(
                arguments,
                dict,
            ):
                raise ValueError(
                    "tool arguments must be an object"
                )

            return AgentDecision(
                decision_type="tool",
                tool_call=ToolCall(
                    tool_name=tool_name,
                    arguments=arguments,
                ),
            )

        raise ValueError(
            f"unsupported decision type: "
            f"{decision_type}"
        )