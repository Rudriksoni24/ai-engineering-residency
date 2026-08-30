import pytest

from agents.tools.banking import (
    GetAccountTool,
    GetTransactionTool,
)
from agents.tools.registry import (
    AgentToolRegistry,
)


def create_account_tool():

    return GetAccountTool(
        accounts={}
    )


def create_transaction_tool():

    return GetTransactionTool(
        transactions={}
    )


def test_registers_tool():

    registry = AgentToolRegistry()

    registry.register(
        create_account_tool()
    )

    assert len(registry) == 1

    assert registry.names() == [
        "get_account"
    ]


def test_registers_multiple_tools():

    registry = AgentToolRegistry(
        tools=[
            create_account_tool(),
            create_transaction_tool(),
        ]
    )

    assert registry.names() == [
        "get_account",
        "get_transaction",
    ]


def test_gets_registered_tool():

    tool = create_account_tool()

    registry = AgentToolRegistry(
        tools=[tool]
    )

    assert (
        registry.get(
            "get_account"
        )
        is tool
    )


def test_unknown_tool_returns_none():

    registry = AgentToolRegistry()

    assert (
        registry.get(
            "missing_tool"
        )
        is None
    )


def test_require_rejects_unknown_tool():

    registry = AgentToolRegistry()

    with pytest.raises(
        ValueError,
        match=(
            "unknown tool requested"
        ),
    ):
        registry.require(
            "missing_tool"
        )


def test_rejects_duplicate_tools():

    registry = AgentToolRegistry(
        tools=[
            create_account_tool()
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "tool already registered"
        ),
    ):
        registry.register(
            create_account_tool()
        )


def test_exposes_definitions():

    registry = AgentToolRegistry(
        tools=[
            create_account_tool()
        ]
    )

    definitions = (
        registry.definitions()
    )

    assert len(definitions) == 1

    assert (
        definitions[0].name
        == "get_account"
    )

    assert (
        definitions[0]
        .parameters[0]
        .name
        == "account_id"
    )