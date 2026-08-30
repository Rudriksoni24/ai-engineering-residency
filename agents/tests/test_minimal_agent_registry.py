import pytest

from agents.core.decision_parser import (
    AgentDecisionParser,
)
from agents.core.minimal_agent import (
    MinimalAgent,
)
from agents.core.prompt_builder import (
    AgentPromptBuilder,
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


class FakeGenerator:

    def __init__(
        self,
        response: str,
    ) -> None:

        self.response = response
        self.last_prompt: str | None = None

    def generate(
        self,
        prompt: str,
    ) -> str:

        self.last_prompt = prompt

        return self.response


def build_agent(
    response: str,
):

    generator = FakeGenerator(
        response
    )

    registry = AgentToolRegistry(
        tools=[
            GetAccountTool(
                accounts={
                    "ACC001": {
                        "owner": (
                            "Ravi Sharma"
                        ),
                        "account_type": (
                            "savings"
                        ),
                        "balance": 125000,
                        "currency": "INR",
                    }
                }
            ),
            GetTransactionTool(
                transactions={
                    "TXN9001": {
                        "account_id": (
                            "ACC001"
                        ),
                        "amount": 2500,
                        "currency": "INR",
                        "status": (
                            "completed"
                        ),
                    }
                }
            ),
        ]
    )

    executor = AgentToolExecutor(
        registry
    )

    agent = MinimalAgent(
        generator=generator,
        registry=registry,
        executor=executor,
        prompt_builder=(
            AgentPromptBuilder()
        ),
        decision_parser=(
            AgentDecisionParser()
        ),
    )

    return agent, generator


def test_agent_executes_account_tool():

    agent, _ = build_agent(
        """
        {
          "type": "tool",
          "tool_name": "get_account",
          "arguments": {
            "account_id": "ACC001"
          }
        }
        """
    )

    response = agent.run(
        "Show account ACC001."
    )

    assert (
        response.tool_used
        == "get_account"
    )

    assert (
        "Ravi Sharma"
        in response.answer
    )


def test_agent_executes_transaction_tool():

    agent, _ = build_agent(
        """
        {
          "type": "tool",
          "tool_name": "get_transaction",
          "arguments": {
            "transaction_id": "TXN9001"
          }
        }
        """
    )

    response = agent.run(
        "Show transaction TXN9001."
    )

    assert (
        response.tool_used
        == "get_transaction"
    )

    assert (
        "2500"
        in response.answer
    )


def test_prompt_contains_registry_tools():

    agent, generator = build_agent(
        """
        {
          "type": "final",
          "answer": "Hello."
        }
        """
    )

    agent.run("Hello")

    assert (
        generator.last_prompt
        is not None
    )

    assert (
        "get_account"
        in generator.last_prompt
    )

    assert (
        "get_transaction"
        in generator.last_prompt
    )

    assert (
        "transaction_id"
        in generator.last_prompt
    )


def test_agent_rejects_invalid_arguments():

    agent, _ = build_agent(
        """
        {
          "type": "tool",
          "tool_name": "get_account",
          "arguments": {
            "account_id": 123
          }
        }
        """
    )

    with pytest.raises(
        ValueError,
        match=(
            "must be a non-empty string"
        ),
    ):
        agent.run(
            "Show account 123."
        )