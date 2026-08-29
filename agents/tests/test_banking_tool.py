import pytest

from agents.tools.banking import (
    GetAccountTool,
)


def create_tool() -> GetAccountTool:

    return GetAccountTool(
        accounts={
            "ACC001": {
                "owner": "Ravi Sharma",
                "account_type": "savings",
                "balance": 125000,
                "currency": "INR",
            }
        }
    )


def test_gets_account():

    tool = create_tool()

    result = tool.execute(
        {
            "account_id": "ACC001"
        }
    )

    assert "ACC001" in result
    assert "Ravi Sharma" in result
    assert "125000" in result
    assert "INR" in result


def test_unknown_account():

    tool = create_tool()

    result = tool.execute(
        {
            "account_id": "ACC999"
        }
    )

    assert (
        result
        == "Account ACC999 was not found."
    )


def test_account_id_required():

    tool = create_tool()

    with pytest.raises(
        ValueError,
        match="account_id is required",
    ):
        tool.execute({})