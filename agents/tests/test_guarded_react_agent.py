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
                "no fake response available"
            )

        return self.responses.pop(0)


def build_agent(
    *,
    responses: list[str],
    guard: AgentDecisionGuard,
    memory: AgentMemory | None = None,
) -> ReActAgent:
    registry = AgentToolRegistry()

    registry.register(
        GetAccountTool(
            accounts=ACCOUNTS
        )
    )

    generator = FakeGenerator(
        responses
    )

    return ReActAgent(
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
        max_iterations=5,
        memory=memory,
        decision_guard=guard,
    )


def test_guarded_agent_accepts_final_answer():
    agent = build_agent(
        responses=[
            """
            {
              "type": "final",
              "answer": "Hello!"
            }
            """
        ],
        guard=AgentDecisionGuard(),
    )

    response = agent.run(
        "Say hello."
    )

    assert (
        response.answer
        == "Hello!"
    )


def test_guarded_agent_rejects_unknown_tool():
    agent = build_agent(
        responses=[
            """
            {
              "type": "tool",
              "tool_name": "unknown_tool",
              "arguments": {}
            }
            """
        ],
        guard=AgentDecisionGuard(),
    )

    with pytest.raises(
        AgentExecutionError
    ) as exc_info:
        agent.run(
            "Use an unknown tool."
        )

    message = str(
        exc_info.value
    )

    assert "rejected" in message
    assert "unknown_tool" in message


def test_guarded_agent_rejects_blocked_tool():
    guard = AgentDecisionGuard(
        config=AgentGuardrailConfig(
            blocked_tools=frozenset(
                {
                    "get_account",
                }
            )
        )
    )

    agent = build_agent(
        responses=[
            """
            {
              "type": "tool",
              "tool_name": "get_account",
              "arguments": {
                "account_id": "ACC001"
              }
            }
            """
        ],
        guard=guard,
    )

    with pytest.raises(
        AgentExecutionError
    ) as exc_info:
        agent.run(
            "Who owns ACC001?"
        )

    assert (
        "blocked"
        in str(exc_info.value)
    )


def test_guardrail_failure_does_not_commit_memory():
    memory = AgentMemory()

    guard = AgentDecisionGuard(
        config=AgentGuardrailConfig(
            blocked_tools=frozenset(
                {
                    "get_account",
                }
            )
        )
    )

    agent = build_agent(
        responses=[
            """
            {
              "type": "tool",
              "tool_name": "get_account",
              "arguments": {
                "account_id": "ACC001"
              }
            }
            """
        ],
        guard=guard,
        memory=memory,
    )

    with pytest.raises(
        AgentExecutionError
    ):
        agent.run(
            "Who owns ACC001?"
        )

    assert (
        memory.messages()
        == ()
    )


def test_answer_length_guard_is_enforced():
    guard = AgentDecisionGuard(
        config=AgentGuardrailConfig(
            max_final_answer_chars=5
        )
    )

    agent = build_agent(
        responses=[
            """
            {
              "type": "final",
              "answer": "This answer is too long."
            }
            """
        ],
        guard=guard,
    )

    with pytest.raises(
        AgentExecutionError
    ) as exc_info:
        agent.run(
            "Answer."
        )

    assert (
        "maximum length"
        in str(exc_info.value)
    )


def test_guardrails_remain_optional():
    registry = AgentToolRegistry()

    registry.register(
        GetAccountTool(
            accounts=ACCOUNTS
        )
    )

    generator = FakeGenerator(
        [
            """
            {
              "type": "final",
              "answer": "Backward compatible."
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
        decision_guard=None,
    )

    response = agent.run(
        "Hello."
    )

    assert (
        response.answer
        == "Backward compatible."
    )