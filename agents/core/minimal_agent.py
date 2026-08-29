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
from agents.tools.base import AgentTool


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
        tools: list[AgentTool],
        prompt_builder: AgentPromptBuilder,
        decision_parser: AgentDecisionParser,
    ) -> None:

        self.generator = generator
        self.prompt_builder = prompt_builder
        self.decision_parser = decision_parser

        self.tools = {
            tool.name: tool
            for tool in tools
        }

    def run(
        self,
        user_query: str,
    ) -> AgentResponse:

        prompt = self.prompt_builder.build(
            user_query=user_query,
            tools=list(
                self.tools.values()
            ),
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

        tool = self.tools.get(
            tool_call.tool_name
        )

        if tool is None:
            raise ValueError(
                "unknown tool requested: "
                f"{tool_call.tool_name}"
            )

        observation = tool.execute(
            tool_call.arguments
        )

        return AgentResponse(
            answer=observation,
            tool_used=tool.name,
            observation=observation,
        )