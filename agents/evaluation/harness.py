from typing import Protocol

from agents.contracts.agent import (
    AgentResponse,
)
from agents.evaluation.contracts import (
    AgentEvaluationCase,
    AgentEvaluationResult,
)


class EvaluatableAgent(
    Protocol
):
    def run(
        self,
        user_query: str,
    ) -> AgentResponse:
        ...


class AgentEvaluationHarness:
    def evaluate(
        self,
        *,
        agent: EvaluatableAgent,
        case: AgentEvaluationCase,
    ) -> AgentEvaluationResult:
        try:
            response = agent.run(
                case.user_query
            )
        except Exception as exc:
            return self._evaluate_failure(
                case=case,
                error=exc,
            )

        return self._evaluate_success(
            case=case,
            response=response,
        )

    def evaluate_many(
        self,
        *,
        agent: EvaluatableAgent,
        cases: list[AgentEvaluationCase]
        | tuple[AgentEvaluationCase, ...],
    ) -> tuple[AgentEvaluationResult, ...]:
        return tuple(
            self.evaluate(
                agent=agent,
                case=case,
            )
            for case in cases
        )

    def _evaluate_success(
        self,
        *,
        case: AgentEvaluationCase,
        response: AgentResponse,
    ) -> AgentEvaluationResult:
        actual_tools = tuple(
            step.tool_name
            for step in response.steps
        )

        checks: list[
            tuple[str, bool]
        ] = []

        checks.append(
            (
                "expected_success",
                case.expected_success,
            )
        )

        answer_lower = (
            response.answer.lower()
        )

        keyword_check = all(
            keyword.lower()
            in answer_lower
            for keyword
            in case.required_answer_keywords
        )

        checks.append(
            (
                "required_answer_keywords",
                keyword_check,
            )
        )

        expected_tools_check = all(
            tool_name
            in actual_tools
            for tool_name
            in case.expected_tools
        )

        checks.append(
            (
                "expected_tools",
                expected_tools_check,
            )
        )

        if (
            case.expected_tool_sequence
            is None
        ):
            sequence_check = True
        else:
            sequence_check = (
                actual_tools
                == case.expected_tool_sequence
            )

        checks.append(
            (
                "expected_tool_sequence",
                sequence_check,
            )
        )

        if case.max_steps is None:
            step_check = True
        else:
            step_check = (
                len(response.steps)
                <= case.max_steps
            )

        checks.append(
            (
                "max_steps",
                step_check,
            )
        )

        passed = all(
            passed
            for _, passed in checks
        )

        return AgentEvaluationResult(
            case_id=case.case_id,
            passed=passed,
            answer=response.answer,
            actual_tools=actual_tools,
            step_count=len(
                response.steps
            ),
            error=None,
            checks=tuple(checks),
        )

    def _evaluate_failure(
        self,
        *,
        case: AgentEvaluationCase,
        error: Exception,
    ) -> AgentEvaluationResult:
        error_message = str(error)

        checks: list[
            tuple[str, bool]
        ] = []

        checks.append(
            (
                "expected_failure",
                not case.expected_success,
            )
        )

        error_lower = (
            error_message.lower()
        )

        error_keyword_check = all(
            keyword.lower()
            in error_lower
            for keyword
            in case.expected_error_keywords
        )

        checks.append(
            (
                "expected_error_keywords",
                error_keyword_check,
            )
        )

        passed = all(
            passed
            for _, passed in checks
        )

        return AgentEvaluationResult(
            case_id=case.case_id,
            passed=passed,
            answer=None,
            actual_tools=(),
            step_count=0,
            error=error_message,
            checks=tuple(checks),
        )