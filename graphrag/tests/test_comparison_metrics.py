from graphrag.comparison.metrics import (
    keyword_coverage,
    tokenize,
)


def test_tokenize_normalizes_text():

    assert tokenize(
        "ACC001 initiated TXN9001."
    ) == {
        "acc001",
        "initiated",
        "txn9001",
    }


def test_keyword_coverage_full_match():

    score = keyword_coverage(
        expected_answer=(
            "ACC001 initiated TXN9001"
        ),
        actual_answer=(
            "ACC001 initiated TXN9001"
        ),
    )

    assert score == 1.0


def test_keyword_coverage_partial_match():

    score = keyword_coverage(
        expected_answer=(
            "ACC001 initiated TXN9001"
        ),
        actual_answer=(
            "ACC001 initiated a "
            "transaction"
        ),
    )

    assert 0.0 < score < 1.0


def test_empty_expected_answer():

    score = keyword_coverage(
        expected_answer="",
        actual_answer="anything",
    )

    assert score == 1.0