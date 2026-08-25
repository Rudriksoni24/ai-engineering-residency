from benchmarks.benchmark_types import BenchmarkCase


BENCHMARK_CASES = [
    BenchmarkCase(
        name="transformer_concept",
        prompt=(
            "Explain self-attention in three concise bullet points."
        ),
        expected_keywords=(
            "query",
            "key",
            "value",
        ),
    ),
    BenchmarkCase(
        name="rag_concept",
        prompt=(
            "Explain retrieval augmented generation in three concise "
            "bullet points."
        ),
        expected_keywords=(
            "retrieval",
            "context",
            "generation",
        ),
    ),
    BenchmarkCase(
        name="structured_output",
        prompt=(
            "Return only valid JSON with the following structure:\n"
            '{"transaction_id": "string", '
            '"risk_level": "low|medium|high", '
            '"reason": "string"}'
        ),
        expects_json=True,
    ),
    BenchmarkCase(
        name="banking_reasoning",
        prompt=(
            "A customer normally spends $100 per transaction but suddenly "
            "attempts a $10,000 transaction from a new country. "
            "List five factors that should be evaluated before blocking it."
        ),
        expected_keywords=(
            "history",
            "location",
            "merchant",
            "authentication",
            "transaction",
        ),
    ),
    BenchmarkCase(
        name="concise_summary",
        prompt=(
            "Summarize why quantization is useful for local LLM inference "
            "in exactly three bullet points."
        ),
        expected_keywords=(
            "memory",
            "speed",
            "precision",
        ),
    ),
]