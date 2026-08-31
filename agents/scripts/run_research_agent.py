from agents.apps.research_agent import (
    ResearchAnalysisAgent,
)
from agents.evaluation.contracts import (
    AgentEvaluationCase,
)
from agents.evaluation.harness import (
    AgentEvaluationHarness,
)
from agents.evaluation.metrics import (
    summarize_results,
)
from agents.generation.ollama_generator import (
    OllamaAgentGenerator,
)
from agents.memory.store import (
    AgentMemory,
)


def build_agent() -> ResearchAnalysisAgent:
    memory = AgentMemory(
        max_messages=6
    )

    return ResearchAnalysisAgent(
        generator=OllamaAgentGenerator(
            model="qwen2.5:3b"
        ),
        max_iterations=15,
        memory=memory,
    )


def main() -> None:
    agent = build_agent()

    query = (
        "Compare the responsibility of the "
        "agent decision guard with the tool "
        "executor. Use the knowledge tools "
        "to verify the answer before responding."
    )

    response = agent.run(
        query
    )

    print(
        f"\nQuestion: {query}"
    )

    print(
        f"\nAnswer: {response.answer}"
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

    print(
        "\n=== EVALUATION ==="
    )

    evaluation_agent = build_agent()

    case = AgentEvaluationCase(
        case_id=(
            "research-guard-vs-executor"
        ),
        user_query=(
            "Compare the responsibility of "
            "the decision guard and tool "
            "executor. Use the available "
            "knowledge tools to verify both."
        ),
        required_answer_keywords=(
            "guard",
            "executor",
            "policy",
        ),
        expected_tools=(
            "search_knowledge",
            "read_document",
        ),
        max_steps=6,
    )

    harness = AgentEvaluationHarness()

    result = harness.evaluate(
        agent=evaluation_agent,
        case=case,
    )

    print(
        f"Case: {result.case_id}"
    )

    print(
        f"Passed: {result.passed}"
    )

    print(
        f"Answer: {result.answer}"
    )

    print(
        f"Tools: {result.actual_tools}"
    )

    print(
        f"Steps: {result.step_count}"
    )

    if result.error is not None:
        print(
            f"Error: {result.error}"
        )

    print(
        "Checks:"
    )

    for (
        check_name,
        check_passed,
    ) in result.checks:
        print(
            f"  {check_name}: "
            f"{check_passed}"
        )

    summary = summarize_results(
        [result]
    )

    print(
        "\nSummary:"
    )

    print(
        f"Pass rate: "
        f"{summary.pass_rate:.2%}"
    )


if __name__ == "__main__":
    main()