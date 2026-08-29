import pytest

from agents.contracts.agent import (
    AgentDecision,
    ToolCall,
)


def test_tool_call_creation():

    call = ToolCall(
        tool_name="get_account",
        arguments={
            "account_id": "ACC001"
        },
    )

    assert (
        call.tool_name
        == "get_account"
    )


def test_tool_call_requires_name():

    with pytest.raises(
        ValueError,
        match="tool_name cannot be empty",
    ):
        ToolCall(
            tool_name=""
        )


def test_final_decision():

    decision = AgentDecision(
        decision_type="final",
        final_answer="Hello",
    )

    assert (
        decision.final_answer
        == "Hello"
    )


def test_tool_decision_requires_call():

    with pytest.raises(
        ValueError,
        match=(
            "tool decision requires "
            "tool_call"
        ),
    ):
        AgentDecision(
            decision_type="tool"
        )