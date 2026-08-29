import pytest

from graphrag.generation.prompt_builder import (
    GraphRAGPromptBuilder,
)


def test_builds_grounded_prompt():

    builder = GraphRAGPromptBuilder()

    prompt = builder.build(
        query=(
            "What transaction did "
            "ACC001 initiate?"
        ),
        graph_context=(
            "ACC001 [account] "
            "--[initiated]--> "
            "TXN001 [transaction]"
        ),
    )

    assert (
        "ACC001 [account]"
        in prompt
    )

    assert (
        "--[initiated]-->"
        in prompt
    )

    assert (
        "What transaction did "
        "ACC001 initiate?"
        in prompt
    )

    assert (
        "using only the graph "
        "knowledge"
        in prompt
    )


def test_rejects_empty_query():

    builder = GraphRAGPromptBuilder()

    with pytest.raises(
        ValueError,
        match="query cannot be empty",
    ):
        builder.build(
            query="",
            graph_context="context",
        )


def test_rejects_empty_context():

    builder = GraphRAGPromptBuilder()

    with pytest.raises(
        ValueError,
        match=(
            "graph_context cannot "
            "be empty"
        ),
    ):
        builder.build(
            query="question",
            graph_context="",
        )