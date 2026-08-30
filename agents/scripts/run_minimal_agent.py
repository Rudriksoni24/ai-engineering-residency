import os

from agents.core.decision_parser import (
    AgentDecisionParser,
)
from agents.core.minimal_agent import (
    MinimalAgent,
)
from agents.core.prompt_builder import (
    AgentPromptBuilder,
)
from agents.generation.ollama_generator import (
    OllamaAgentGenerator,
)
from agents.tools.banking import (
    GetAccountTool,
)
from agents.tools.executor import (
    AgentToolExecutor,
)
from agents.tools.registry import (
    AgentToolRegistry,
)


def build_agent(
    model: str,
) -> MinimalAgent:

    accounts = {
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

    account_tool = GetAccountTool(
    accounts=accounts
)

    registry = AgentToolRegistry(
        tools=[
            account_tool
        ]
    )

    executor = AgentToolExecutor(
        registry
    )

    return MinimalAgent(
        generator=(
            OllamaAgentGenerator(
                model=model
            )
        ),
        registry=registry,
        executor=executor,
        prompt_builder=(
            AgentPromptBuilder()
        ),
        decision_parser=(
            AgentDecisionParser()
        ),
    )


def main() -> None:

    model = os.getenv(
        "OLLAMA_MODEL"
    )

    if not model:
        raise RuntimeError(
            "OLLAMA_MODEL is not set."
        )

    agent = build_agent(
        model=model
    )

    questions = [
        "Say hello in one sentence.",
        "Show me account ACC001.",
        "Show me account ACC999.",
    ]

    print("=" * 70)
    print(
        "SPRINT 5 DAY 1 — "
        "MINIMAL TOOL-USING AGENT"
    )
    print("=" * 70)

    print(
        f"\nModel: {model}"
    )

    for index, question in enumerate(
        questions,
        start=1,
    ):

        print("\n" + "-" * 70)

        print(
            f"Question {index}: "
            f"{question}"
        )

        response = agent.run(
            question
        )

        print(
            f"\nAnswer:\n"
            f"{response.answer}"
        )

        print(
            "\nTool used: "
            f"{response.tool_used}"
        )

        if response.observation:
            print(
                "\nObservation:"
            )
            print(
                response.observation
            )

    print("\n" + "=" * 70)
    print(
        "Minimal agent completed."
    )
    print("=" * 70)


if __name__ == "__main__":
    main()