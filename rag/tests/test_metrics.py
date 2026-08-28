from rag.evaluation.metrics import (
    context_coverage,
    keyword_recall,
)


def test_keyword_recall_exact_match():
    score = keyword_recall(
        expected_answer="Transaction mismatches must be investigated",
        generated_answer="Transaction mismatches must be investigated",
    )

    assert score == 1.0


def test_keyword_recall_partial_match():
    score = keyword_recall(
        expected_answer="Transaction mismatches must be investigated",
        generated_answer="Mismatches must be investigated",
    )

    assert 0.0 < score < 1.0


def test_keyword_recall_empty_expected_answer():
    score = keyword_recall(
        expected_answer="",
        generated_answer="Anything",
    )

    assert score == 1.0


def test_context_coverage_fully_supported():
    score = context_coverage(
        generated_answer="Transaction mismatches must be investigated",
        retrieved_documents=[
            "All transaction mismatches must be investigated."
        ],
    )

    assert score == 1.0


def test_context_coverage_empty_answer():
    score = context_coverage(
        generated_answer="",
        retrieved_documents=[
            "Some context"
        ],
    )

    assert score == 0.0


def test_context_coverage_partially_supported():
    score = context_coverage(
        generated_answer=(
            "Transaction mismatches must be investigated "
            "by the finance team"
        ),
        retrieved_documents=[
            "Transaction mismatches must be investigated."
        ],
    )

    assert 0.0 < score < 1.0