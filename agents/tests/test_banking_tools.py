from agents.tools.banking import (
    GetAccountTool,
    GetTransactionTool,
)


def test_account_tool_definition():

    tool = GetAccountTool(
        accounts={}
    )

    definition = (
        tool.definition
    )

    assert (
        definition.name
        == "get_account"
    )

    assert (
        definition.parameters[0].name
        == "account_id"
    )


def test_transaction_tool():

    tool = GetTransactionTool(
        transactions={
            "TXN9001": {
                "account_id": "ACC001",
                "amount": 2500,
                "currency": "INR",
                "status": "completed",
            }
        }
    )

    result = tool.execute(
        {
            "transaction_id": (
                "TXN9001"
            )
        }
    )

    assert "TXN9001" in result
    assert "ACC001" in result
    assert "2500" in result
    assert "completed" in result


def test_unknown_transaction():

    tool = GetTransactionTool(
        transactions={}
    )

    result = tool.execute(
        {
            "transaction_id": (
                "TXN9999"
            )
        }
    )

    assert (
        result
        == (
            "Transaction TXN9999 "
            "was not found."
        )
    )