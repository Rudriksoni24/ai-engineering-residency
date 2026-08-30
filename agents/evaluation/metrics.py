from dataclasses import dataclass

from agents.evaluation.contracts import (
    AgentEvaluationResult,
)


@dataclass(frozen=True)
class AgentEvaluationSummary:
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    average_steps: float


def summarize_results(
    results: list[AgentEvaluationResult]
    | tuple[AgentEvaluationResult, ...],
) -> AgentEvaluationSummary:
    total_cases = len(results)

    if total_cases == 0:
        return AgentEvaluationSummary(
            total_cases=0,
            passed_cases=0,
            failed_cases=0,
            pass_rate=0.0,
            average_steps=0.0,
        )

    passed_cases = sum(
        1
        for result in results
        if result.passed
    )

    failed_cases = (
        total_cases
        - passed_cases
    )

    total_steps = sum(
        result.step_count
        for result in results
    )

    return AgentEvaluationSummary(
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        pass_rate=(
            passed_cases / total_cases
        ),
        average_steps=(
            total_steps / total_cases
        ),
    )