import pytest

from agents.core.decision_parser import (
    AgentDecisionParser,
)
from agents.core.prompt_builder import (
    AgentPromptBuilder,
)
from agents.core.react_agent import (
    AgentExecutionError,
    ReActAgent,
)
from agents.memory.store import (
    AgentMemory,
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

ACCOUNTS = {
    "ACC001": {
        "owner": "Ravi Sharma",
        "account_type": "savings",
        "balance": 125000,
        "currency": "INR",
    },
}

class FakeGenerator:
    def __init__(
        self,
        responses: list[str],
    ) -> None:
        self.responses = list(
            responses
        )
        self.prompts: list[str] = []

    def generate(
        self,
        prompt: str,
    ) -> str:
        self.prompts.append(
            prompt
        )

        if not self.responses:
            raise RuntimeError(
                "no fake response "
                "available"
            )

        return self.responses.pop(0)


def build_agent(
    generator: FakeGenerator,
    memory: AgentMemory,
) -> ReActAgent:
    registry = AgentToolRegistry()

    registry.register(
        GetAccountTool(accounts=ACCOUNTS)
    )

    executor = AgentToolExecutor(
        registry=registry
    )

    return ReActAgent(
        generator=generator,
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


def test_successful_turn_is_committed():
    memory = AgentMemory()

    generator = FakeGenerator(
        responses=[
            """
            {
              "type": "final",
              "answer": "Hello!"
            }
            """
        ]
    )

    agent = build_agent(
        generator=generator,
        memory=memory,
    )

    response = agent.run(
        "Say hello."
    )

    assert response.answer == "Hello!"

    messages = memory.messages()

    assert len(messages) == 2

    assert messages[0].role == "user"
    assert (
        messages[0].content
        == "Say hello."
    )

    assert (
        messages[1].role
        == "assistant"
    )

    assert (
        messages[1].content
        == "Hello!"
    )


def test_previous_turn_is_in_next_prompt():
    memory = AgentMemory()

    generator = FakeGenerator(
        responses=[
            """
            {
              "type": "final",
              "answer":
                "ACC001 belongs to Ravi Sharma."
            }
            """,
            """
            {
              "type": "final",
              "answer":
                "The remembered account is ACC001."
            }
            """,
        ]
    )

    agent = build_agent(
        generator=generator,
        memory=memory,
    )

    agent.run(
        "Who owns ACC001?"
    )

    agent.run(
        "Which account were "
        "we discussing?"
    )

    assert len(
        generator.prompts
    ) == 2

    second_prompt = (
        generator.prompts[1]
    )

    assert (
        "Who owns ACC001?"
        in second_prompt
    )

    assert (
        "ACC001 belongs to "
        "Ravi Sharma."
        in second_prompt
    )


def test_current_turn_not_in_old_memory():
    memory = AgentMemory()

    generator = FakeGenerator(
        responses=[
            """
            {
              "type": "final",
              "answer": "Done."
            }
            """
        ]
    )

    agent = build_agent(
        generator=generator,
        memory=memory,
    )

    agent.run(
        "Current question"
    )

    first_prompt = (
        generator.prompts[0]
    )

    memory_section_start = (
        first_prompt.index(
            "Conversation memory"
        )
    )

    query_section_start = (
        first_prompt.index(
            "Current user query"
        )
    )

    memory_section = (
        first_prompt[
            memory_section_start:
            query_section_start
        ]
    )

    assert (
        "Current question"
        not in memory_section
    )


def test_failed_execution_is_not_committed():
    memory = AgentMemory()

    generator = FakeGenerator(
        responses=[
            """
            {
              "type": "tool",
              "tool_name":
                "does_not_exist",
              "arguments": {}
            }
            """
        ]
    )

    agent = build_agent(
        generator=generator,
        memory=memory,
    )

    with pytest.raises(
        AgentExecutionError
    ):
        agent.run(
            "Run an invalid tool."
        )

    assert memory.messages() == ()


def test_memory_remains_optional():
    registry = AgentToolRegistry()

    registry.register(
        GetAccountTool(accounts=ACCOUNTS)
    )

    generator = FakeGenerator(
        responses=[
            """
            {
              "type": "final",
              "answer": "No memory required."
            }
            """
        ]
    )

    agent = ReActAgent(
        generator=generator,
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
        memory=None,
    )

    response = agent.run(
        "Hello"
    )

    assert (
        response.answer
        == "No memory required."
    )