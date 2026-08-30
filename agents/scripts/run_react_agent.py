from __future__ import annotations

from agents.core.decision_parser import AgentDecisionParser
from agents.core.prompt_builder import AgentPromptBuilder
from agents.core.react_agent import ReActAgent
from agents.generation.ollama_generator import OllamaAgentGenerator
from agents.tools.banking import GetAccountTool, GetTransactionTool
from agents.tools.executor import AgentToolExecutor
from agents.tools.registry import AgentToolRegistry

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
        GetAccountTool(accounts=ACCOUNTS)
    )
    registry.register(
        GetTransactionTool(transactions=TRANSACTIONS)
    )

    executor = AgentToolExecutor(registry=registry)

    generator = OllamaAgentGenerator(
        model="qwen2.5:3b",
    )

    return ReActAgent(
        generator=generator,
        registry=registry,
        executor=executor,
        prompt_builder=AgentPromptBuilder(),
        decision_parser=AgentDecisionParser(),
        max_iterations=5,
    )


def main() -> None:
    agent = build_agent()

    query = (
        "Who owns the account connected to transaction TXN9001? "
        "Use the available tools to determine the answer."
    )

    response = agent.run(query)

    print("\nUSER GOAL")
    print(query)

    print("\nFINAL ANSWER")
    print(response.answer)

    print("\nEXECUTION TRACE")

    if not response.steps:
        print("No tools were used.")
        return

    for step in response.steps:
        print(f"\nIteration: {step.iteration}")
        print(f"Tool: {step.tool_name}")
        print(f"Arguments: {step.arguments}")
        print(f"Observation: {step.observation}")


if __name__ == "__main__":
    main()