from __future__ import annotations

import json

import pytest

from agents.core.decision_parser import AgentDecisionParser
from agents.core.prompt_builder import AgentPromptBuilder
from agents.core.react_agent import (
    AgentExecutionError,
    AgentIterationLimitError,
    ReActAgent,
)
from agents.tools.banking import GetAccountTool, GetTransactionTool
from agents.tools.executor import AgentToolExecutor
from agents.tools.registry import AgentToolRegistry

ACCOUNTS = {
    "ACC001": {
        "owner": "Ravi Sharma",
        "account_type": "savings",
        "balance": 125000,
        "currency": "INR",
    }
}


TRANSACTIONS = {
    "TXN9001": {
        "account_id": "ACC001",
        "amount": 2500,
        "currency": "INR",
        "status": "completed",
    }
}


class FakeGenerator:
    def __init__(self, outputs: list[str]) -> None:
        self._outputs = list(outputs)
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)

        if not self._outputs:
            raise AssertionError(
                "FakeGenerator received more calls than expected"
            )

        return self._outputs.pop(0)


def tool_decision(
    tool_name: str,
    arguments: dict[str, object],
) -> str:
    return json.dumps(
        {
            "type": "tool",
            "tool_name": tool_name,
            "arguments": arguments,
        }
    )


def final_decision(answer: str) -> str:
    return json.dumps(
        {
            "type": "final",
            "answer": answer,
        }
    )


def build_agent(
    outputs: list[str],
    max_iterations: int = 5,
) -> tuple[ReActAgent, FakeGenerator]:
    registry = AgentToolRegistry()

    registry.register(
        GetAccountTool(accounts=ACCOUNTS)
    )
    registry.register(
        GetTransactionTool(transactions=TRANSACTIONS)
    )

    executor = AgentToolExecutor(registry=registry)
    generator = FakeGenerator(outputs)

    agent = ReActAgent(
        generator=generator,
        registry=registry,
        executor=executor,
        prompt_builder=AgentPromptBuilder(),
        decision_parser=AgentDecisionParser(),
        max_iterations=max_iterations,
    )

    return agent, generator


def test_direct_final_answer_requires_zero_tool_calls() -> None:
    agent, generator = build_agent(
        [
            final_decision(
                "No tool is required for this response."
            )
        ]
    )

    response = agent.run("Say whether you can answer directly.")

    assert response.answer == "No tool is required for this response."
    assert response.steps == ()
    assert len(generator.prompts) == 1


def test_one_tool_request_then_final_answer() -> None:
    agent, generator = build_agent(
        [
            tool_decision(
                "get_account",
                {"account_id": "ACC001"},
            ),
            final_decision(
                "ACC001 is owned by Ravi Sharma."
            ),
        ]
    )

    response = agent.run("Who owns ACC001?")

    assert response.answer == "ACC001 is owned by Ravi Sharma."
    assert len(response.steps) == 1

    step = response.steps[0]

    assert step.iteration == 1
    assert step.tool_name == "get_account"
    assert step.arguments == {"account_id": "ACC001"}
    assert "Ravi Sharma" in step.observation

    assert len(generator.prompts) == 2


def test_two_tool_sequence_uses_second_tool_after_first_observation() -> None:
    agent, generator = build_agent(
        [
            tool_decision(
                "get_transaction",
                {"transaction_id": "TXN9001"},
            ),
            tool_decision(
                "get_account",
                {"account_id": "ACC001"},
            ),
            final_decision(
                "The account connected to TXN9001 is owned by Ravi Sharma."
            ),
        ]
    )

    response = agent.run(
        "Who owns the account connected to transaction TXN9001?"
    )

    assert response.answer == (
        "The account connected to TXN9001 is owned by Ravi Sharma."
    )

    assert len(response.steps) == 2

    first = response.steps[0]
    second = response.steps[1]

    assert first.iteration == 1
    assert first.tool_name == "get_transaction"
    assert first.arguments == {
        "transaction_id": "TXN9001"
    }
    assert "ACC001" in first.observation

    assert second.iteration == 2
    assert second.tool_name == "get_account"
    assert second.arguments == {
        "account_id": "ACC001"
    }
    assert "Ravi Sharma" in second.observation

    assert len(generator.prompts) == 3


def test_observation_is_fed_into_subsequent_model_call() -> None:
    agent, generator = build_agent(
        [
            tool_decision(
                "get_transaction",
                {"transaction_id": "TXN9001"},
            ),
            final_decision(
                "TXN9001 belongs to ACC001."
            ),
        ]
    )

    response = agent.run(
        "Which account is connected to TXN9001?"
    )

    assert len(response.steps) == 1
    assert len(generator.prompts) == 2

    first_observation = response.steps[0].observation

    assert first_observation in generator.prompts[1]
    assert "get_transaction" in generator.prompts[1]
    assert "TXN9001" in generator.prompts[1]


def test_unknown_tool_call_becomes_controlled_failure() -> None:
    agent, _ = build_agent(
        [
            tool_decision(
                "transfer_everything",
                {"account_id": "ACC001"},
            )
        ]
    )

    with pytest.raises(AgentExecutionError) as exc_info:
        agent.run("Execute an unavailable tool.")

    assert "transfer_everything" in str(exc_info.value)


def test_invalid_tool_arguments_become_controlled_failure() -> None:
    agent, _ = build_agent(
        [
            tool_decision(
                "get_account",
                {"wrong_argument": "ACC001"},
            )
        ]
    )

    with pytest.raises(AgentExecutionError) as exc_info:
        agent.run("Who owns ACC001?")

    assert "get_account" in str(exc_info.value)


def test_maximum_iteration_limit_stops_endless_tool_requests() -> None:
    agent, generator = build_agent(
        [
            tool_decision(
                "get_account",
                {"account_id": "ACC001"},
            ),
            tool_decision(
                "get_account",
                {"account_id": "ACC001"},
            ),
            tool_decision(
                "get_account",
                {"account_id": "ACC001"},
            ),
        ],
        max_iterations=3,
    )

    with pytest.raises(AgentIterationLimitError) as exc_info:
        agent.run("Keep requesting the same tool.")

    assert "maximum iteration limit" in str(exc_info.value).lower()
    assert len(generator.prompts) == 3


def test_execution_trace_is_preserved() -> None:
    agent, _ = build_agent(
        [
            tool_decision(
                "get_transaction",
                {"transaction_id": "TXN9001"},
            ),
            tool_decision(
                "get_account",
                {"account_id": "ACC001"},
            ),
            final_decision(
                "Ravi Sharma owns the account."
            ),
        ]
    )

    response = agent.run(
        "Who owns the account connected to TXN9001?"
    )

    assert [step.iteration for step in response.steps] == [1, 2]

    assert [step.tool_name for step in response.steps] == [
        "get_transaction",
        "get_account",
    ]

    assert response.steps[0].arguments == {
        "transaction_id": "TXN9001"
    }

    assert response.steps[1].arguments == {
        "account_id": "ACC001"
    }

    assert "ACC001" in response.steps[0].observation
    assert "Ravi Sharma" in response.steps[1].observation