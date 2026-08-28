from rag.generation.prompt_builder import (
    PromptBuilder,
)
from rag.retrieval.types import RetrievalResult


def create_result() -> RetrievalResult:
    return RetrievalResult(
        id="chunk-1",
        content=(
            "Transaction mismatches must be "
            "investigated before reconciliation."
        ),
        source="reconciliation_policy.txt",
        score=0.95,
        metadata={},
    )


def test_prompt_contains_query():
    builder = PromptBuilder()

    prompt = builder.build(
        query="How are mismatches handled?",
        context=[create_result()],
    )

    assert (
        "How are mismatches handled?"
        in prompt
    )


def test_prompt_contains_context():
    builder = PromptBuilder()

    prompt = builder.build(
        query="Test question",
        context=[create_result()],
    )

    assert (
        "Transaction mismatches must be"
        in prompt
    )


def test_prompt_contains_source():
    builder = PromptBuilder()

    prompt = builder.build(
        query="Test question",
        context=[create_result()],
    )

    assert (
        "reconciliation_policy.txt"
        in prompt
    )


def test_empty_context():
    builder = PromptBuilder()

    prompt = builder.build(
        query="Test question",
        context=[],
    )

    assert (
        "No relevant context was retrieved."
        in prompt
    )