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
    generator: FakeGenerator,
) -> MinimalAgent:

    tool = GetAccountTool(
        accounts={
            "ACC001": {
                "owner": "Ravi Sharma",
                "account_type": "savings",
                "balance": 125000,
                "currency": "INR",
            }
        }
    )

    return MinimalAgent(
        generator=generator,
        tools=[tool],
        prompt_builder=(
            AgentPromptBuilder()
        ),
        decision_parser=(
            AgentDecisionParser()
        ),
    )


def test_agent_returns_direct_answer():

    generator = FakeGenerator(
        """
        {
          "type": "final",
          "answer": "Hello!"
        }
        """
    )

    agent = build_agent(
        generator
    )

    response = agent.run(
        "Say hello."
    )

    assert (
        response.answer
        == "Hello!"
    )

    assert response.tool_used is None
    assert response.observation is None


def test_agent_executes_tool():

    generator = FakeGenerator(
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

    agent = build_agent(
        generator
    )

    response = agent.run(
        "Show account ACC001."
    )

    assert (
        response.tool_used
        == "get_account"
    )

    assert (
        response.observation
        is not None
    )

    assert (
        "Ravi Sharma"
        in response.answer
    )


def test_unknown_tool_is_rejected():

    generator = FakeGenerator(
        """
        {
          "type": "tool",
          "tool_name": "delete_account",
          "arguments": {}
        }
        """
    )

    agent = build_agent(
        generator
    )

    with pytest.raises(
        ValueError,
        match=(
            "unknown tool requested"
        ),
    ):
        agent.run(
            "Delete ACC001"
        )


def test_prompt_contains_available_tool():

    generator = FakeGenerator(
        """
        {
          "type": "final",
          "answer": "Done."
        }
        """
    )

    agent = build_agent(
        generator
    )

    agent.run(
        "Say hello."
    )

    assert (
        generator.last_prompt
        is not None
    )

    assert (
        "get_account"
        in generator.last_prompt
    )