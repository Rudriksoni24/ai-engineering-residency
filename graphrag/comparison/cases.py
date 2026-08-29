from graphrag.comparison.contracts import (
    ComparisonCase,
)


BANKING_COMPARISON_CASES = [
    ComparisonCase(
        case_id="direct-001",
        query=(
            "What transaction was "
            "initiated by ACC001?"
        ),
        expected_answer=(
            "ACC001 initiated TXN9001."
        ),
        query_type="relationship",
    ),
    ComparisonCase(
        case_id="entity-001",
        query=(
            "Which account is owned "
            "by Ravi Sharma?"
        ),
        expected_answer=(
            "Ravi Sharma owns ACC001."
        ),
        query_type="relationship",
    ),
]