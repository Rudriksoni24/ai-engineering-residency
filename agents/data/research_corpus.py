RESEARCH_CORPUS = {
    "doc-react": {
        "title": "ReAct Agent Loop",
        "content": (
            "A ReAct-style agent repeatedly decides whether to call a tool "
            "or return a final answer. Tool observations are added to the "
            "current execution trajectory so later decisions can use evidence "
            "collected earlier in the same run. The application owns the "
            "maximum iteration budget."
        ),
    },
    "doc-tool-execution": {
        "title": "Agent Tool Execution",
        "content": (
            "The tool executor resolves registered tools and validates the "
            "specific tool execution contract. It checks required arguments, "
            "argument types, and undeclared arguments before executing the "
            "tool. Runtime exceptions are converted into controlled tool "
            "failures."
        ),
    },
    "doc-memory": {
        "title": "Agent Memory",
        "content": (
            "Agent memory is application-owned state from earlier completed "
            "conversation turns. It is different from the current execution "
            "trajectory. Successful user and assistant turns may be committed "
            "to memory, while failed agent runs should not be committed."
        ),
    },
    "doc-guardrails": {
        "title": "Agent Guardrails",
        "content": (
            "An agent decision guard applies deterministic application policy "
            "after structured model output has been parsed but before tool "
            "execution. It can reject unknown or blocked tools and enforce "
            "configured limits. A model-generated tool request is not "
            "execution permission."
        ),
    },
    "doc-evaluation": {
        "title": "Agent Evaluation",
        "content": (
            "Agent evaluation measures complete behavioral outcomes. "
            "Deterministic evaluation can inspect required answer keywords, "
            "expected tool usage, tool trajectories, maximum step counts, and "
            "expected controlled failures. Evaluation remains separate from "
            "runtime agent logic."
        ),
    },
}