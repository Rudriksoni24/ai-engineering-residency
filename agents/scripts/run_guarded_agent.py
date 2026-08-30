from agents.core.decision_parser import (
    AgentDecisionParser,
)
from agents.core.prompt_builder import (
    AgentPromptBuilder,
)
from agents.core.react_agent import (
    ReActAgent,
)
from agents.generation.ollama_generator import (
    OllamaAgentGenerator,
)
from agents.guardrails.contracts import (
    AgentGuardrailConfig,
)
from agents.guardrails.decision_guard import (
    AgentDecisionGuard,
)
from agents.memory.store import (
    AgentMemory,
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


def main() -> None:
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

    executor = AgentToolExecutor(
        registry=registry
    )

    guard = AgentDecisionGuard(
        config=AgentGuardrailConfig(
            max_final_answer_chars=1000,
            max_tool_arguments=3,
            blocked_tools=frozenset(),
        )
    )

    memory = AgentMemory(
        max_messages=6
    )

    agent = ReActAgent(
        generator=OllamaAgentGenerator(
            model="qwen2.5:3b"
        ),
        registry=registry,
        executor=executor,
        prompt_builder=(
            AgentPromptBuilder()
        ),
        decision_parser=(
            AgentDecisionParser()
        ),
        max_iterations=5,
        memory=memory,
        decision_guard=guard,
    )

    query = (
        "Who owns the account associated "
        "with transaction TXN9001?"
    )

    response = agent.run(
        query
    )

    print(
        f"Answer: {response.answer}"
    )

    print(
        "\nExecution steps:"
    )

    for step in response.steps:
        print(
            f"{step.iteration}. "
            f"{step.tool_name} "
            f"{step.arguments}"
        )

        print(
            f"   observation: "
            f"{step.observation}"
        )


if __name__ == "__main__":
    main()