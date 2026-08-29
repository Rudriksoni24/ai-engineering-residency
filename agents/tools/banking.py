from typing import Any


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
    def name(self) -> str:
        return "get_account"

    @property
    def description(self) -> str:
        return (
            "Retrieve banking account "
            "information using an account ID."
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
            account_id
        )

        if account is None:
            return (
                f"Account {account_id} "
                "was not found."
            )

        owner = account.get(
            "owner",
            "unknown",
        )

        account_type = account.get(
            "account_type",
            "unknown",
        )

        balance = account.get(
            "balance",
            "unknown",
        )

        currency = account.get(
            "currency",
            "unknown",
        )

        return (
            f"Account {account_id}: "
            f"owner={owner}, "
            f"type={account_type}, "
            f"balance={balance}, "
            f"currency={currency}"
        )