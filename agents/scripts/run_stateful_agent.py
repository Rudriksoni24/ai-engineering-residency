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
        GetAccountTool(accounts=ACCOUNTS)
    )

    registry.register(
        GetTransactionTool(transactions=TRANSACTIONS)
    )

    executor = AgentToolExecutor(
        registry=registry
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
    )

    first_query = (
        "Use the available tools to "
        "look up ACC001 and tell me "
        "who owns that account."
    )

    print(
        "\n--- TURN 1 ---"
    )

    print(
        f"User: {first_query}"
    )

    first_response = (
        agent.run(first_query)
    )

    print(
        f"Agent: "
        f"{first_response.answer}"
    )

    print(
        "\nMemory after turn 1:"
    )

    for message in memory.messages():
        print(
            f"{message.role}: "
            f"{message.content}"
        )

    second_query = (
        "What is the balance of that "
        "same account?"
    )

    print(
        "\n--- TURN 2 ---"
    )

    print(
        f"User: {second_query}"
    )

    second_response = (
        agent.run(second_query)
    )

    print(
        f"Agent: "
        f"{second_response.answer}"
    )

    print(
        "\nMemory after turn 2:"
    )

    for message in memory.messages():
        print(
            f"{message.role}: "
            f"{message.content}"
        )


if __name__ == "__main__":
    main()