from agents.contracts.agent import AgentDecision
from agents.guardrails.contracts import (
    AgentGuardrailConfig,
)
from agents.tools.registry import (
    AgentToolRegistry,
)


class AgentGuardrailError(
    ValueError
):
    pass


class AgentDecisionGuard:
    def __init__(
        self,
        *,
        config: AgentGuardrailConfig | None = None,
    ) -> None:
        self.config = (
            config
            if config is not None
            else AgentGuardrailConfig()
        )

    def validate(
        self,
        *,
        decision: AgentDecision,
        registry: AgentToolRegistry,
    ) -> None:
        if decision.decision_type == "final":
            self._validate_final(
                decision
            )
            return

        if decision.decision_type == "tool":
            self._validate_tool(
                decision=decision,
                registry=registry,
            )
            return

        raise AgentGuardrailError(
            "unsupported decision type: "
            f"{decision.decision_type}"
        )

    def _validate_final(
        self,
        decision: AgentDecision,
    ) -> None:
        answer = decision.final_answer

        if answer is None:
            raise AgentGuardrailError(
                "final decision missing answer"
            )

        normalized_answer = answer.strip()

        if not normalized_answer:
            raise AgentGuardrailError(
                "final answer cannot be empty"
            )

        if (
            len(normalized_answer)
            > self.config.max_final_answer_chars
        ):
            raise AgentGuardrailError(
                "final answer exceeds maximum "
                f"length of "
                f"{self.config.max_final_answer_chars}"
            )

    def _validate_tool(
        self,
        *,
        decision: AgentDecision,
        registry: AgentToolRegistry,
    ) -> None:
        tool_call = decision.tool_call

        if tool_call is None:
            raise AgentGuardrailError(
                "tool decision missing tool call"
            )

        tool_name = tool_call.tool_name

        if tool_name in self.config.blocked_tools:
            raise AgentGuardrailError(
                f"tool '{tool_name}' is blocked "
                "by agent policy"
            )

        if tool_name not in registry.names():
            raise AgentGuardrailError(
                f"tool '{tool_name}' is not "
                "registered"
            )

        argument_count = len(
            tool_call.arguments
        )

        if (
            argument_count
            > self.config.max_tool_arguments
        ):
            raise AgentGuardrailError(
                f"tool '{tool_name}' requested "
                f"{argument_count} arguments; "
                "maximum allowed is "
                f"{self.config.max_tool_arguments}"
            )