from agents.contracts.agent import (
    AgentDecision,
    AgentResponse,
    AgentStep,
)
from agents.core.decision_parser import (
    AgentDecisionParser,
)
from agents.core.prompt_builder import (
    AgentPromptBuilder,
)
from agents.guardrails.decision_guard import (
    AgentDecisionGuard,
    AgentGuardrailError,
)
from agents.memory.store import AgentMemory
from agents.tools.executor import (
    AgentToolExecutor,
)
from agents.tools.registry import (
    AgentToolRegistry,
)


class AgentExecutionError(
    RuntimeError
):
    pass


class AgentIterationLimitError(
    RuntimeError
):
    pass


class ReActAgent:
    def __init__(
        self,
        *,
        generator,
        registry: AgentToolRegistry,
        executor: AgentToolExecutor,
        prompt_builder: AgentPromptBuilder,
        decision_parser: AgentDecisionParser,
        max_iterations: int = 5,
        memory: AgentMemory | None = None,
        decision_guard: AgentDecisionGuard | None = None,
    ) -> None:
        if max_iterations <= 0:
            raise ValueError(
                "max_iterations must be "
                "greater than zero"
            )

        self.generator = generator
        self.registry = registry
        self.executor = executor
        self.prompt_builder = prompt_builder
        self.decision_parser = decision_parser
        self.max_iterations = max_iterations
        self.memory = memory
        self.decision_guard = decision_guard

    def run(
        self,
        user_query: str,
    ) -> AgentResponse:
        normalized_query = (
            user_query.strip()
        )

        if not normalized_query:
            raise ValueError(
                "user_query cannot be empty"
            )

        steps: list[AgentStep] = []

        memory_messages = (
            self.memory.messages()
            if self.memory is not None
            else ()
        )

        for iteration in range(
            1,
            self.max_iterations + 1,
        ):
            prompt = (
                self.prompt_builder.build(
                    user_query=normalized_query,
                    registry=self.registry,
                    steps=steps,
                    memory=memory_messages,
                )
            )

            raw_decision = (
                self.generator.generate(
                    prompt
                )
            )

            decision = (
                self.decision_parser.parse(
                    raw_decision
                )
            )

            self._validate_decision(
                decision
            )

            if (
                decision.decision_type
                == "final"
            ):
                response = (
                    self._build_final_response(
                        decision=decision,
                        steps=steps,
                    )
                )

                self._commit_memory(
                    user_query=normalized_query,
                    response=response,
                )

                return response

            tool_call = (
                decision.tool_call
            )

            if tool_call is None:
                raise AgentExecutionError(
                    "tool decision missing tool call"
                )

            result = (
                self.executor.execute(
                    tool_name=tool_call.tool_name,
                    arguments=tool_call.arguments,
                )
            )

            if not result.success:
                error_message = (
                    result.error
                    or "tool execution failed"
                )

                raise AgentExecutionError(
                    f"tool '{tool_call.tool_name}' "
                    f"failed: {error_message}"
                )

            steps.append(
                AgentStep(
                    iteration=iteration,
                    tool_name=result.tool_name,
                    arguments=dict(
                        tool_call.arguments
                    ),
                    observation=result.observation,
                )
            )

        raise AgentIterationLimitError(
            "agent exceeded maximum "
            f"iteration limit of "
            f"{self.max_iterations}"
        )

    def _validate_decision(
        self,
        decision: AgentDecision,
    ) -> None:
        if self.decision_guard is None:
            return

        try:
            self.decision_guard.validate(
                decision=decision,
                registry=self.registry,
            )
        except AgentGuardrailError as exc:
            raise AgentExecutionError(
                f"agent decision rejected: {exc}"
            ) from exc

    def _commit_memory(
        self,
        *,
        user_query: str,
        response: AgentResponse,
    ) -> None:
        if self.memory is None:
            return

        self.memory.remember_user(
            user_query
        )

        self.memory.remember_assistant(
            response.answer
        )

    @staticmethod
    def _build_final_response(
        *,
        decision: AgentDecision,
        steps: list[AgentStep],
    ) -> AgentResponse:
        final_answer = (
            decision.final_answer
        )

        if final_answer is None:
            raise AgentExecutionError(
                "final decision missing answer"
            )

        last_step = (
            steps[-1]
            if steps
            else None
        )

        return AgentResponse(
            answer=final_answer,
            tool_used=(
                last_step.tool_name
                if last_step
                else None
            ),
            observation=(
                last_step.observation
                if last_step
                else None
            ),
            steps=tuple(steps),
        )