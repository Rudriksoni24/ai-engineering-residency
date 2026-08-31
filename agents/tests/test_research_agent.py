import json

from agents.apps.research_agent import (
    ResearchAnalysisAgent,
)
from agents.memory.store import (
    AgentMemory,
)


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


def tool_decision(
    tool_name: str,
    arguments: dict[str, str],
) -> str:
    return json.dumps(
        {
            "type": "tool",
            "tool_name": tool_name,
            "arguments": arguments,
        }
    )


def final_decision(
    answer: str,
) -> str:
    return json.dumps(
        {
            "type": "final",
            "answer": answer,
        }
    )


def test_research_agent_can_search_read_and_answer():
    generator = FakeGenerator(
        [
            tool_decision(
                "search_knowledge",
                {
                    "query": (
                        "agent guardrails policy"
                    )
                },
            ),
            tool_decision(
                "read_document",
                {
                    "document_id": (
                        "doc-guardrails"
                    )
                },
            ),
            final_decision(
                (
                    "Agent guardrails apply "
                    "deterministic application "
                    "policy before tool execution."
                )
            ),
        ]
    )

    agent = ResearchAnalysisAgent(
        generator=generator,
        max_iterations=5,
    )

    response = agent.run(
        "What is the purpose of "
        "agent guardrails?"
    )

    assert (
        "deterministic application policy"
        in response.answer
    )

    assert (
        tuple(
            step.tool_name
            for step in response.steps
        )
        == (
            "search_knowledge",
            "read_document",
        )
    )


def test_research_agent_can_perform_multi_document_analysis():
    generator = FakeGenerator(
        [
            tool_decision(
                "search_knowledge",
                {
                    "query": (
                        "tool executor validation"
                    )
                },
            ),
            tool_decision(
                "read_document",
                {
                    "document_id": (
                        "doc-tool-execution"
                    )
                },
            ),
            tool_decision(
                "search_knowledge",
                {
                    "query": (
                        "agent guardrails policy"
                    )
                },
            ),
            tool_decision(
                "read_document",
                {
                    "document_id": (
                        "doc-guardrails"
                    )
                },
            ),
            final_decision(
                (
                    "The executor validates the "
                    "specific tool execution contract, "
                    "while the decision guard applies "
                    "application policy before execution."
                )
            ),
        ]
    )

    agent = ResearchAnalysisAgent(
        generator=generator,
        max_iterations=6,
    )

    response = agent.run(
        (
            "Compare the responsibility "
            "of the tool executor and "
            "the decision guard."
        )
    )

    assert (
        "executor"
        in response.answer.lower()
    )

    assert (
        "decision guard"
        in response.answer.lower()
    )

    actual_tools = tuple(
        step.tool_name
        for step in response.steps
    )

    assert actual_tools == (
        "search_knowledge",
        "read_document",
        "search_knowledge",
        "read_document",
    )


def test_successful_research_commits_memory():
    memory = AgentMemory(
        max_messages=4
    )

    generator = FakeGenerator(
        [
            tool_decision(
                "search_knowledge",
                {
                    "query": (
                        "agent evaluation"
                    )
                },
            ),
            tool_decision(
                "read_document",
                {
                    "document_id": (
                        "doc-evaluation"
                    )
                },
            ),
            final_decision(
                (
                    "Agent evaluation measures "
                    "complete behavioral outcomes."
                )
            ),
        ]
    )

    agent = ResearchAnalysisAgent(
        generator=generator,
        memory=memory,
    )

    response = agent.run(
        "What does agent evaluation measure?"
    )

    assert (
        response.answer
        == (
            "Agent evaluation measures "
            "complete behavioral outcomes."
        )
    )

    messages = memory.messages()

    assert len(messages) == 2

    assert (
        messages[0].role
        == "user"
    )

    assert (
        messages[1].role
        == "assistant"
    )


def test_guardrails_are_applied_to_integrated_agent():
    generator = FakeGenerator(
        [
            tool_decision(
                "unknown_research_tool",
                {},
            )
        ]
    )

    agent = ResearchAnalysisAgent(
        generator=generator,
    )

    try:
        agent.run(
            "Use an unknown research tool."
        )
    except Exception as exc:
        message = str(exc)

        assert (
            "rejected"
            in message
        )

        assert (
            "unknown_research_tool"
            in message
        )
    else:
        raise AssertionError(
            "expected guarded agent failure"
        )