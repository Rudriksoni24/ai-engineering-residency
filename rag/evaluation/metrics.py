import re
from typing import Iterable


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"\b\w+\b", text.lower())
        if token
    }


def keyword_recall(
    expected_answer: str,
    generated_answer: str,
) -> float:
    expected_tokens = tokenize(expected_answer)

    if not expected_tokens:
        return 1.0

    generated_tokens = tokenize(generated_answer)

    matched = expected_tokens.intersection(generated_tokens)

    return len(matched) / len(expected_tokens)


def context_coverage(
    generated_answer: str,
    retrieved_documents: Iterable[str],
) -> float:
    context_tokens = tokenize(
        " ".join(retrieved_documents)
    )

    generated_tokens = tokenize(generated_answer)

    if not generated_tokens:
        return 0.0

    supported_tokens = generated_tokens.intersection(
        context_tokens
    )

    return len(supported_tokens) / len(generated_tokens)