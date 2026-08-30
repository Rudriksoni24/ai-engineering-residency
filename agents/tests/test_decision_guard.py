import pytest

from agents.contracts.agent import (
    AgentDecision,
    ToolCall,
)
from agents.guardrails.contracts import (
    AgentGuardrailConfig,
)
from agents.guardrails.decision_guard import (
    AgentDecisionGuard,
    AgentGuardrailError,
)
from agents.tools.banking import (
    GetAccountTool,
)
from agents.tools.registry import (
    AgentToolRegistry,
)


ACCOUNTS = {
    "ACC001": {
        "owner": "Ravi Sharma",
        "account_type": "savings",
        "balance": 125000,
        "currency": "INR",
    },
}


def build_registry() -> AgentToolRegistry:
    registry = AgentToolRegistry()

    registry.register(
        GetAccountTool(
            accounts=ACCOUNTS
        )
    )

    return registry


def test_valid_final_decision_is_allowed():
    guard = AgentDecisionGuard()
    registry = build_registry()

    decision = AgentDecision(
        decision_type="final",
        final_answer="Hello.",
        tool_call=None,
    )

    guard.validate(
        decision=decision,
        registry=registry,
    )


def test_final_answer_length_is_guarded():
    guard = AgentDecisionGuard(
        config=AgentGuardrailConfig(
            max_final_answer_chars=5
        )
    )

    registry = build_registry()

    decision = AgentDecision(
        decision_type="final",
        final_answer="Too long",
        tool_call=None,
    )

    with pytest.raises(
        AgentGuardrailError
    ) as exc_info:
        guard.validate(
            decision=decision,
            registry=registry,
        )

    assert (
        "maximum length"
        in str(exc_info.value)
    )


def test_registered_tool_is_allowed():
    guard = AgentDecisionGuard()
    registry = build_registry()

    decision = AgentDecision(
        decision_type="tool",
        final_answer=None,
        tool_call=ToolCall(
            tool_name="get_account",
            arguments={
                "account_id": "ACC001",
            },
        ),
    )

    guard.validate(
        decision=decision,
        registry=registry,
    )


def test_unknown_tool_is_rejected():
    guard = AgentDecisionGuard()
    registry = build_registry()

    decision = AgentDecision(
        decision_type="tool",
        final_answer=None,
        tool_call=ToolCall(
            tool_name="unknown_tool",
            arguments={},
        ),
    )

    with pytest.raises(
        AgentGuardrailError
    ) as exc_info:
        guard.validate(
            decision=decision,
            registry=registry,
        )

    assert (
        "not registered"
        in str(exc_info.value)
    )


def test_blocked_tool_is_rejected():
    guard = AgentDecisionGuard(
        config=AgentGuardrailConfig(
            blocked_tools=frozenset(
                {
                    "get_account",
                }
            )
        )
    )

    registry = build_registry()

    decision = AgentDecision(
        decision_type="tool",
        final_answer=None,
        tool_call=ToolCall(
            tool_name="get_account",
            arguments={
                "account_id": "ACC001",
            },
        ),
    )

    with pytest.raises(
        AgentGuardrailError
    ) as exc_info:
        guard.validate(
            decision=decision,
            registry=registry,
        )

    assert (
        "blocked"
        in str(exc_info.value)
    )


def test_excessive_argument_count_is_rejected():
    guard = AgentDecisionGuard(
        config=AgentGuardrailConfig(
            max_tool_arguments=1
        )
    )

    registry = build_registry()

    decision = AgentDecision(
        decision_type="tool",
        final_answer=None,
        tool_call=ToolCall(
            tool_name="get_account",
            arguments={
                "account_id": "ACC001",
                "unexpected": "value",
            },
        ),
    )

    with pytest.raises(
        AgentGuardrailError
    ) as exc_info:
        guard.validate(
            decision=decision,
            registry=registry,
        )

    assert (
        "maximum allowed"
        in str(exc_info.value)
    )


def test_invalid_guardrail_config_is_rejected():
    with pytest.raises(
        ValueError
    ):
        AgentGuardrailConfig(
            max_final_answer_chars=0
        )

    with pytest.raises(
        ValueError
    ):
        AgentGuardrailConfig(
            max_tool_arguments=-1
        )