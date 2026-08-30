from agents.core.prompt_builder import (
    AgentPromptBuilder,
)
from agents.memory.contracts import (
    MemoryMessage,
)
from agents.tools.banking import (
    GetAccountTool,
)
from agents.tools.registry import (
    AgentToolRegistry,
)

ACCOUNTS = {
        "ACC001": {
            "owner": "Ravi Sharma",
            "account_type": "savings",
            "balance": 125000,
            "currency": "INR",
        },
    }

def test_prompt_contains_previous_memory():
    registry = AgentToolRegistry()

    registry.register(
        GetAccountTool(accounts=ACCOUNTS)
    )

    builder = AgentPromptBuilder()

    memory = (
        MemoryMessage(
            role="user",
            content=(
                "Look up ACC001."
            ),
        ),
        MemoryMessage(
            role="assistant",
            content=(
                "ACC001 belongs to "
                "Ravi Sharma."
            ),
        ),
    )

    prompt = builder.build(
        user_query=(
            "What is the balance "
            "of that same account?"
        ),
        registry=registry,
        memory=memory,
    )

    assert (
        "Look up ACC001."
        in prompt
    )

    assert (
        "Ravi Sharma"
        in prompt
    )

    assert (
        "What is the balance "
        "of that same account?"
        in prompt
    )