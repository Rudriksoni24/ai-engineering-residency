import pytest

from agents.tools.contracts import (
    ToolDefinition,
    ToolParameter,
    ToolResult,
)


def test_tool_parameter():

    parameter = ToolParameter(
        name="account_id",
        parameter_type="string",
        description="Bank account ID.",
    )

    assert (
        parameter.name
        == "account_id"
    )

    assert parameter.required


def test_tool_parameter_requires_name():

    with pytest.raises(
        ValueError,
        match=(
            "parameter name "
            "cannot be empty"
        ),
    ):
        ToolParameter(
            name="",
            parameter_type="string",
            description="test",
        )


def test_tool_definition():

    definition = ToolDefinition(
        name="get_account",
        description=(
            "Retrieve an account."
        ),
    )

    assert (
        definition.name
        == "get_account"
    )


def test_tool_result_success():

    result = ToolResult(
        tool_name="get_account",
        success=True,
        observation="Account found.",
    )

    assert result.success
    assert result.error is None