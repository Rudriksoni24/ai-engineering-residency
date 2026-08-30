from agents.tools.banking import (
    GetAccountTool,
    GetTransactionTool,
)
from agents.tools.executor import (
    AgentToolExecutor,
)
from agents.tools.registry import (
    AgentToolRegistry,
)


def main() -> None:

    account_tool = GetAccountTool(
        accounts={
            "ACC001": {
                "owner": "Ravi Sharma",
                "account_type": "savings",
                "balance": 125000,
                "currency": "INR",
            },
            "ACC002": {
                "owner": "Priya Mehta",
                "account_type": "current",
                "balance": 84000,
                "currency": "INR",
            },
        }
    )

    transaction_tool = (
        GetTransactionTool(
            transactions={
                "TXN9001": {
                    "account_id": (
                        "ACC001"
                    ),
                    "amount": 2500,
                    "currency": "INR",
                    "status": "completed",
                },
                "TXN9002": {
                    "account_id": (
                        "ACC002"
                    ),
                    "amount": 7800,
                    "currency": "INR",
                    "status": "pending",
                },
            }
        )
    )

    registry = AgentToolRegistry(
        tools=[
            account_tool,
            transaction_tool,
        ]
    )

    executor = AgentToolExecutor(
        registry
    )

    print("=" * 70)
    print(
        "SPRINT 5 DAY 2 — "
        "AGENT TOOL REGISTRY"
    )
    print("=" * 70)

    print("\nRegistered tools:")

    for definition in (
        registry.definitions()
    ):
        print(
            f"\n- {definition.name}"
        )

        print(
            f"  {definition.description}"
        )

        print(
            "  Parameters:"
        )

        for parameter in (
            definition.parameters
        ):
            required = (
                "required"
                if parameter.required
                else "optional"
            )

            print(
                f"    - "
                f"{parameter.name}: "
                f"{parameter.parameter_type} "
                f"({required})"
            )

    print("\n" + "-" * 70)

    print(
        "\nExecuting get_account:"
    )

    account_result = (
        executor.execute(
            tool_name="get_account",
            arguments={
                "account_id": "ACC001"
            },
        )
    )

    print(
        f"Success: "
        f"{account_result.success}"
    )

    print(
        f"Observation: "
        f"{account_result.observation}"
    )

    print("\n" + "-" * 70)

    print(
        "\nExecuting get_transaction:"
    )

    transaction_result = (
        executor.execute(
            tool_name=(
                "get_transaction"
            ),
            arguments={
                "transaction_id": (
                    "TXN9001"
                )
            },
        )
    )

    print(
        f"Success: "
        f"{transaction_result.success}"
    )

    print(
        "Observation: "
        f"{transaction_result.observation}"
    )

    print("\n" + "-" * 70)

    print(
        "\nInvalid argument example:"
    )

    invalid_result = (
        executor.execute(
            tool_name="get_account",
            arguments={
                "account_id": 123
            },
        )
    )

    print(
        f"Success: "
        f"{invalid_result.success}"
    )

    print(
        f"Error: "
        f"{invalid_result.error}"
    )

    print("\n" + "-" * 70)

    print(
        "\nUnknown tool example:"
    )

    unknown_result = (
        executor.execute(
            tool_name="delete_account",
            arguments={},
        )
    )

    print(
        f"Success: "
        f"{unknown_result.success}"
    )

    print(
        f"Error: "
        f"{unknown_result.error}"
    )

    print("\n" + "=" * 70)
    print(
        "Agent Tool Registry ready."
    )
    print("=" * 70)


if __name__ == "__main__":
    main()