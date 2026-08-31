from agents.core.decision_parser import (
    AgentDecisionParser,
)
from agents.core.prompt_builder import (
    AgentPromptBuilder,
)
from agents.core.react_agent import (
    ReActAgent,
)
from agents.data.research_corpus import (
    RESEARCH_CORPUS,
)
from agents.guardrails.contracts import (
    AgentGuardrailConfig,
)
from agents.guardrails.decision_guard import (
    AgentDecisionGuard,
)
from agents.memory.store import AgentMemory
from agents.tools.executor import (
    AgentToolExecutor,
)
from agents.tools.registry import (
    AgentToolRegistry,
)
from agents.tools.research import (
    ReadDocumentTool,
    SearchKnowledgeTool,
)


class ResearchAnalysisAgent:
    def __init__(
        self,
        *,
        generator,
        max_iterations: int = 6,
        memory: AgentMemory | None = None,
    ) -> None:
        registry = AgentToolRegistry()

        registry.register(
            SearchKnowledgeTool(
                documents=RESEARCH_CORPUS
            )
        )

        registry.register(
            ReadDocumentTool(
                documents=RESEARCH_CORPUS
            )
        )

        executor = AgentToolExecutor(
            registry=registry
        )

        guard = AgentDecisionGuard(
            config=AgentGuardrailConfig(
                max_final_answer_chars=4000,
                max_tool_arguments=2,
                blocked_tools=frozenset(),
            )
        )

        self._agent = ReActAgent(
            generator=generator,
            registry=registry,
            executor=executor,
            prompt_builder=AgentPromptBuilder(),
            decision_parser=AgentDecisionParser(),
            max_iterations=max_iterations,
            memory=memory,
            decision_guard=guard,
        )

    def run(
        self,
        user_query: str,
    ):
        return self._agent.run(
            user_query
        )