from typing import Protocol

from agents.contracts.agent import (
    AgentResponse,
)
from agents.core.decision_parser import (
    AgentDecisionParser,
)
from agents.core.prompt_builder import (
    AgentPromptBuilder,
)
from agents.tools.executor import (
    AgentToolExecutor,
)
from agents.tools.registry import (
    AgentToolRegistry,
)


class TextGenerator(Protocol):

    def generate(
        self,
        prompt: str,
    ) -> str:
        ...


class MinimalAgent:

    def __init__(
        self,
        generator: TextGenerator,
        registry: AgentToolRegistry,
        executor: AgentToolExecutor,
        prompt_builder: AgentPromptBuilder,
        decision_parser: AgentDecisionParser,
    ) -> None:

        self.generator = generator
        self.registry = registry
        self.executor = executor
        self.prompt_builder = (
            prompt_builder
        )
        self.decision_parser = (
            decision_parser
        )

    def run(
        self,
        user_query: str,
    ) -> AgentResponse:

        prompt = self.prompt_builder.build(
            user_query=user_query,
            registry=self.registry,
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

        if (
            decision.decision_type
            == "final"
        ):
            return AgentResponse(
                answer=(
                    decision.final_answer
                    or ""
                ),
                tool_used=None,
                observation=None,
            )

        tool_call = decision.tool_call

        if tool_call is None:
            raise RuntimeError(
                "tool decision missing tool call"
            )

        result = self.executor.execute(
            tool_name=(
                tool_call.tool_name
            ),
            arguments=(
                tool_call.arguments
            ),
        )

        if not result.success:
            raise ValueError(
                result.error
                or "tool execution failed"
            )

        return AgentResponse(
            answer=result.observation,
            tool_used=result.tool_name,
            observation=(
                result.observation
            ),
        )