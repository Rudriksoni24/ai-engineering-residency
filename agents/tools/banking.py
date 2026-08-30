from typing import Any

from agents.tools.contracts import (
    ToolDefinition,
    ToolParameter,
)


class GetAccountTool:

    def __init__(
        self,
        accounts: dict[
            str,
            dict[str, Any],
        ],
    ) -> None:
        self.accounts = accounts

    @property
    def definition(
        self,
    ) -> ToolDefinition:

        return ToolDefinition(
            name="get_account",
            description=(
                "Retrieve banking account "
                "information using an "
                "account ID."
            ),
            parameters=[
                ToolParameter(
                    name="account_id",
                    parameter_type="string",
                    description=(
                        "Bank account ID "
                        "such as ACC001."
                    ),
                )
            ],
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:

        account_id = arguments.get(
            "account_id"
        )

        if not isinstance(
            account_id,
            str,
        ) or not account_id.strip():
            raise ValueError(
                "account_id is required"
            )

        account = self.accounts.get(
            account_id.strip()
        )

        if account is None:
            return (
                f"Account {account_id} "
                "was not found."
            )

        return (
            f"Account {account_id}: "
            f"owner="
            f"{account.get('owner', 'unknown')}, "
            f"type="
            f"{account.get('account_type', 'unknown')}, "
            f"balance="
            f"{account.get('balance', 'unknown')}, "
            f"currency="
            f"{account.get('currency', 'unknown')}"
        )


class GetTransactionTool:

    def __init__(
        self,
        transactions: dict[
            str,
            dict[str, Any],
        ],
    ) -> None:
        self.transactions = transactions

    @property
    def definition(
        self,
    ) -> ToolDefinition:

        return ToolDefinition(
            name="get_transaction",
            description=(
                "Retrieve transaction "
                "information using a "
                "transaction ID."
            ),
            parameters=[
                ToolParameter(
                    name="transaction_id",
                    parameter_type="string",
                    description=(
                        "Transaction ID "
                        "such as TXN9001."
                    ),
                )
            ],
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:

        transaction_id = arguments.get(
            "transaction_id"
        )

        if not isinstance(
            transaction_id,
            str,
        ) or not transaction_id.strip():
            raise ValueError(
                "transaction_id is required"
            )

        transaction = (
            self.transactions.get(
                transaction_id.strip()
            )
        )

        if transaction is None:
            return (
                f"Transaction "
                f"{transaction_id} "
                "was not found."
            )

        return (
            f"Transaction {transaction_id}: "
            f"account_id="
            f"{transaction.get('account_id', 'unknown')}, "
            f"amount="
            f"{transaction.get('amount', 'unknown')}, "
            f"currency="
            f"{transaction.get('currency', 'unknown')}, "
            f"status="
            f"{transaction.get('status', 'unknown')}"
        )