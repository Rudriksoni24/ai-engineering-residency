from agents.tools.banking import (
    GetAccountTool,
)
from agents.tools.executor import (
    AgentToolExecutor,
)
from agents.tools.registry import (
    AgentToolRegistry,
)


def create_executor():

    tool = GetAccountTool(
        accounts={
            "ACC001": {
                "owner": "Ravi Sharma",
                "account_type": "savings",
                "balance": 125000,
                "currency": "INR",
            }
        }
    )

    registry = AgentToolRegistry(
        tools=[tool]
    )

    return AgentToolExecutor(
        registry
    )


def test_executes_valid_tool():

    executor = create_executor()

    result = executor.execute(
        tool_name="get_account",
        arguments={
            "account_id": "ACC001"
        },
    )

    assert result.success

    assert (
        "Ravi Sharma"
        in result.observation
    )


def test_unknown_tool_returns_failure():

    executor = create_executor()

    result = executor.execute(
        tool_name="delete_account",
        arguments={},
    )

    assert not result.success

    assert result.error is not None

    assert (
        "unknown tool requested"
        in result.error
    )


def test_missing_required_argument():

    executor = create_executor()

    result = executor.execute(
        tool_name="get_account",
        arguments={},
    )

    assert not result.success

    assert (
        result.error
        == (
            "missing required argument: "
            "account_id"
        )
    )


def test_rejects_wrong_argument_type():

    executor = create_executor()

    result = executor.execute(
        tool_name="get_account",
        arguments={
            "account_id": 123
        },
    )

    assert not result.success

    assert (
        "must be a non-empty string"
        in (result.error or "")
    )


def test_rejects_unknown_argument():

    executor = create_executor()

    result = executor.execute(
        tool_name="get_account",
        arguments={
            "account_id": "ACC001",
            "password": "secret",
        },
    )

    assert not result.success

    assert (
        result.error
        == (
            "unknown tool arguments: "
            "password"
        )
    )