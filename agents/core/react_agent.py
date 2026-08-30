from __future__ import annotations

from agents.contracts.agent import (
    AgentDecision,
    AgentGenerator,
    AgentResponse,
    AgentStep,
)
from agents.core.decision_parser import AgentDecisionParser
from agents.core.prompt_builder import AgentPromptBuilder
from agents.tools.executor import AgentToolExecutor
from agents.tools.registry import AgentToolRegistry


class AgentExecutionError(RuntimeError):
    """Raised when an iterative agent run cannot continue safely."""


class AgentIterationLimitError(AgentExecutionError):
    """Raised when the agent does not terminate within its iteration limit."""


class ReActAgent:
    def __init__(
        self,
        generator: AgentGenerator,
        registry: AgentToolRegistry,
        executor: AgentToolExecutor,
        prompt_builder: AgentPromptBuilder,
        decision_parser: AgentDecisionParser,
        max_iterations: int = 5,
    ) -> None:
        if max_iterations <= 0:
            raise ValueError("max_iterations must be greater than zero")

        self._generator = generator
        self._registry = registry
        self._executor = executor
        self._prompt_builder = prompt_builder
        self._decision_parser = decision_parser
        self._max_iterations = max_iterations

    def run(self, user_query: str) -> AgentResponse:
        if not user_query.strip():
            raise ValueError("user_query must not be empty")

        steps: list[AgentStep] = []

        for iteration in range(1, self._max_iterations + 1):
            prompt = self._prompt_builder.build(
                user_query=user_query,
                registry=self._registry,
                steps=steps,
            )

            raw_output = self._generator.generate(prompt)
            decision = self._decision_parser.parse(raw_output)

            if decision.decision_type == "final":
                return self._build_final_response(
                    decision=decision,
                    steps=steps,
                )

            if decision.decision_type != "tool":
                raise AgentExecutionError(
                    f"Unsupported agent decision: {decision.decision_type}"
                )

            tool_call = decision.tool_call

            if tool_call is None:
                raise AgentExecutionError(
                    "Tool decision did not contain a tool call"
                )

            result = self._executor.execute(
                tool_name=tool_call.tool_name,
                arguments=tool_call.arguments,
            )

            if not result.success:
                message = result.error or "Unknown tool execution error"
                raise AgentExecutionError(
                    f"Tool '{tool_call.tool_name}' failed: {message}"
                )

            steps.append(
                AgentStep(
                    iteration=iteration,
                    tool_name=tool_call.tool_name,
                    arguments=dict(tool_call.arguments),
                    observation=result.observation,
                )
            )

        raise AgentIterationLimitError(
            "Agent reached the maximum iteration limit "
            f"of {self._max_iterations} without producing a final answer"
        )

    @staticmethod
    def _build_final_response(
        decision: AgentDecision,
        steps: list[AgentStep],
    ) -> AgentResponse:
        if decision.final_answer is None:
            raise AgentExecutionError(
                "Final decision did not contain an answer"
            )

        return AgentResponse(
            answer=decision.final_answer,
            steps=tuple(steps),
        )