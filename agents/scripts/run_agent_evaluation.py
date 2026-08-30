from agents.core.decision_parser import (
    AgentDecisionParser,
)
from agents.core.prompt_builder import (
    AgentPromptBuilder,
)
from agents.core.react_agent import (
    ReActAgent,
)
from agents.evaluation.contracts import (
    AgentEvaluationCase,
)
from agents.evaluation.harness import (
    AgentEvaluationHarness,
)
from agents.evaluation.metrics import (
    summarize_results,
)
from agents.generation.ollama_generator import (
    OllamaAgentGenerator,
)
from agents.guardrails.decision_guard import (
    AgentDecisionGuard,
)
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

ACCOUNTS = {
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


TRANSACTIONS = {
    "TXN9001": {
        "account_id": "ACC001",
        "amount": 2500,
        "currency": "INR",
        "status": "completed",
    },
    "TXN9002": {
        "account_id": "ACC002",
        "amount": 7800,
        "currency": "INR",
        "status": "pending",
    },
}


def build_agent() -> ReActAgent:
    registry = AgentToolRegistry()

    registry.register(
        GetAccountTool(
            accounts=ACCOUNTS
        )
    )

    registry.register(
        GetTransactionTool(
            transactions=TRANSACTIONS
        )
    )

    return ReActAgent(
        generator=OllamaAgentGenerator(
            model="qwen2.5:3b"
        ),
        registry=registry,
        executor=AgentToolExecutor(
            registry=registry
        ),
        prompt_builder=(
            AgentPromptBuilder()
        ),
        decision_parser=(
            AgentDecisionParser()
        ),
        decision_guard=(
            AgentDecisionGuard()
        ),
        max_iterations=5,
    )


def main() -> None:
    agent = build_agent()

    cases = (
        AgentEvaluationCase(
            case_id="account-owner",
            user_query=(
                "Who owns ACC001? "
                "Use the available tools "
                "to verify the answer."
            ),
            required_answer_keywords=(
                "Ravi Sharma",
            ),
            expected_tools=(
                "get_account",
            ),
            max_steps=2,
        ),
        AgentEvaluationCase(
            case_id=(
                "transaction-account-owner"
            ),
            user_query=(
                "Who is the owner of the "
                "account associated with "
                "transaction TXN9001? "
                "Use the available tools "
                "to verify both the "
                "transaction and account "
                "owner before answering."
            ),
            required_answer_keywords=(
                "Ravi Sharma",
            ),
            expected_tools=(
                "get_transaction",
                "get_account",
            ),
            expected_tool_sequence=(
                "get_transaction",
                "get_account",
            ),
            max_steps=3,
        ),
        AgentEvaluationCase(
            case_id="transaction-status",
            user_query=(
                "What is the status of "
                "transaction TXN9002?"
            ),
            required_answer_keywords=(
                "pending",
            ),
            expected_tools=(
                "get_transaction",
            ),
            max_steps=2,
        ),
    )

    harness = (
        AgentEvaluationHarness()
    )

    results = harness.evaluate_many(
        agent=agent,
        cases=cases,
    )

    for result in results:
        print(
            f"\nCASE: "
            f"{result.case_id}"
        )

        print(
            f"Passed: "
            f"{result.passed}"
        )

        print(
            f"Answer: "
            f"{result.answer}"
        )

        print(
            f"Tools: "
            f"{result.actual_tools}"
        )

        print(
            f"Steps: "
            f"{result.step_count}"
        )

        if result.error:
            print(
                f"Error: "
                f"{result.error}"
            )

        print(
            "Checks:"
        )

        for (
            check_name,
            check_passed,
        ) in result.checks:
            print(
                f"  {check_name}: "
                f"{check_passed}"
            )

    summary = summarize_results(
        results
    )

    print(
        "\n=== SUMMARY ==="
    )

    print(
        f"Total: "
        f"{summary.total_cases}"
    )

    print(
        f"Passed: "
        f"{summary.passed_cases}"
    )

    print(
        f"Failed: "
        f"{summary.failed_cases}"
    )

    print(
        f"Pass rate: "
        f"{summary.pass_rate:.2%}"
    )

    print(
        f"Average steps: "
        f"{summary.average_steps:.2f}"
    )


if __name__ == "__main__":
    main()