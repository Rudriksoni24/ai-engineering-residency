import re


def tokenize(
    text: str,
) -> set[str]:

    return set(
        re.findall(
            r"[a-z0-9]+",
            text.lower(),
        )
    )


def keyword_coverage(
    expected_answer: str,
    actual_answer: str,
) -> float:

    expected_tokens = tokenize(
        expected_answer
    )

    if not expected_tokens:
        return 1.0

    actual_tokens = tokenize(
        actual_answer
    )

    matched = (
        expected_tokens
        & actual_tokens
    )

    return len(matched) / len(
        expected_tokens
    )