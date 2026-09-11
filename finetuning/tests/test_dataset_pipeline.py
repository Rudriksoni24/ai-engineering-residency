import pytest

from finetuning.data.pipeline import (
    DatasetPipeline,
    DatasetSplit,
    InstructionExample,
    PipelineConfig,
    deduplicate_examples,
    find_split_leakage,
    format_chat_messages,
    format_instruction_example,
    normalize_example,
    normalize_text,
    split_examples,
    validate_no_split_leakage,
    validate_raw_example,
)


def make_example(
    number: int,
) -> InstructionExample:
    return InstructionExample(
        instruction=(
            "Classify transaction status."
        ),
        input_text=(
            f"Transaction TXN-{number:04d}."
        ),
        response=(
            f'{{"transaction_id":"TXN-{number:04d}",'
            '"status":"APPROVED"}'
        ),
    )


def test_valid_example_is_accepted() -> None:
    raw = {
        "instruction": (
            "Classify transaction status."
        ),
        "input": (
            "Transaction TXN-1001 "
            "was declined."
        ),
        "response": (
            '{"status":"DECLINED"}'
        ),
    }

    validate_raw_example(
        raw
    )


def test_missing_instruction_is_rejected() -> None:
    raw = {
        "response": "DECLINED",
    }

    with pytest.raises(
        ValueError,
        match="instruction",
    ):
        validate_raw_example(
            raw
        )


def test_missing_response_is_rejected() -> None:
    raw = {
        "instruction": "Classify this.",
    }

    with pytest.raises(
        ValueError,
        match="response",
    ):
        validate_raw_example(
            raw
        )


def test_empty_instruction_is_rejected() -> None:
    raw = {
        "instruction": "   ",
        "response": "DECLINED",
    }

    with pytest.raises(
        ValueError,
        match="instruction cannot be empty",
    ):
        validate_raw_example(
            raw
        )


def test_empty_response_is_rejected() -> None:
    raw = {
        "instruction": "Classify this.",
        "response": "\n   \t",
    }

    with pytest.raises(
        ValueError,
        match="response cannot be empty",
    ):
        validate_raw_example(
            raw
        )


def test_whitespace_is_normalized() -> None:
    assert normalize_text(
        "  classify   this\n transaction  "
    ) == "classify this transaction"


def test_normalized_example_has_clean_fields() -> None:
    raw = {
        "instruction": (
            "  Classify   transaction. "
        ),
        "input": (
            " TXN-1001   declined. "
        ),
        "response": (
            "  DECLINED  "
        ),
    }

    example = normalize_example(
        raw
    )

    assert (
        example.instruction
        == "Classify transaction."
    )

    assert (
        example.input_text
        == "TXN-1001 declined."
    )

    assert (
        example.response
        == "DECLINED"
    )


def test_optional_input_defaults_to_empty_string() -> None:
    raw = {
        "instruction": "Say hello.",
        "response": "Hello.",
    }

    example = normalize_example(
        raw
    )

    assert example.input_text == ""


def test_duplicate_examples_are_removed() -> None:
    example = make_example(
        1
    )

    unique, duplicate_count = (
        deduplicate_examples(
            [
                example,
                example,
                make_example(2),
            ]
        )
    )

    assert len(unique) == 2
    assert duplicate_count == 1


def test_normalization_allows_semantic_duplicate_detection() -> None:
    first = normalize_example(
        {
            "instruction": (
                "Classify   transaction."
            ),
            "input": "TXN-1 declined.",
            "response": " DECLINED ",
        }
    )

    second = normalize_example(
        {
            "instruction": (
                " Classify transaction. "
            ),
            "input": (
                "TXN-1   declined."
            ),
            "response": "DECLINED",
        }
    )

    assert (
        first.example_id
        == second.example_id
    )


def test_split_is_deterministic() -> None:
    examples = [
        make_example(index)
        for index in range(10)
    ]

    first = split_examples(
        examples,
        validation_ratio=0.2,
        seed=42,
    )

    second = split_examples(
        examples,
        validation_ratio=0.2,
        seed=42,
    )

    assert (
        first.train
        == second.train
    )

    assert (
        first.validation
        == second.validation
    )


def test_different_seed_can_change_split() -> None:
    examples = [
        make_example(index)
        for index in range(20)
    ]

    first = split_examples(
        examples,
        validation_ratio=0.2,
        seed=42,
    )

    second = split_examples(
        examples,
        validation_ratio=0.2,
        seed=99,
    )

    assert (
        first.train
        != second.train
    )


def test_train_and_validation_do_not_overlap() -> None:
    examples = [
        make_example(index)
        for index in range(10)
    ]

    split = split_examples(
        examples,
        validation_ratio=0.2,
        seed=42,
    )

    assert (
        find_split_leakage(split)
        == set()
    )

    validate_no_split_leakage(
        split
    )


def test_explicit_leakage_is_detected() -> None:
    leaked = make_example(
        999
    )

    split = DatasetSplit(
        train=(
            make_example(1),
            leaked,
        ),
        validation=(
            make_example(2),
            leaked,
        ),
    )

    leakage = find_split_leakage(
        split
    )

    assert leaked.example_id in leakage

    with pytest.raises(
        ValueError,
        match="leakage",
    ):
        validate_no_split_leakage(
            split
        )


def test_instruction_format_is_consistent() -> None:
    example = InstructionExample(
        instruction=(
            "Classify transaction."
        ),
        input_text=(
            "TXN-1001 was declined."
        ),
        response='{"status":"DECLINED"}',
    )

    formatted = format_instruction_example(
        example,
        system_prompt=(
            "You are a banking assistant."
        ),
    )

    assert "### System" in formatted
    assert "### Instruction" in formatted
    assert "### Input" in formatted
    assert "### Response" in formatted

    assert (
        '{"status":"DECLINED"}'
        in formatted
    )


def test_empty_input_section_is_omitted() -> None:
    example = InstructionExample(
        instruction="Say hello.",
        input_text="",
        response="Hello.",
    )

    formatted = format_instruction_example(
        example,
        system_prompt="You are helpful.",
    )

    assert "### Input" not in formatted


def test_chat_format_has_required_roles() -> None:
    example = InstructionExample(
        instruction=(
            "Classify transaction."
        ),
        input_text=(
            "TXN-1 was declined."
        ),
        response="DECLINED",
    )

    messages = format_chat_messages(
        example,
        system_prompt=(
            "You are a banking assistant."
        ),
    )

    assert [
        message["role"]
        for message in messages
    ] == [
        "system",
        "user",
        "assistant",
    ]


def test_pipeline_generates_statistics() -> None:
    raw_examples = [
        {
            "instruction": "Classify.",
            "input": "TXN-1 approved.",
            "response": "APPROVED",
        },
        {
            "instruction": "Classify.",
            "input": "TXN-2 declined.",
            "response": "DECLINED",
        },
        {
            "instruction": "Classify.",
            "input": "TXN-3 pending.",
            "response": "PENDING",
        },
        {
            "instruction": "Classify.",
            "input": "TXN-1 approved.",
            "response": "APPROVED",
        },
        {
            "instruction": "",
            "response": "INVALID",
        },
    ]

    pipeline = DatasetPipeline(
        PipelineConfig(
            validation_ratio=0.33,
            seed=42,
        )
    )

    result = pipeline.process(
        raw_examples
    )

    statistics = result.statistics

    assert statistics.raw_examples == 5

    assert (
        statistics.valid_examples_before_deduplication
        == 4
    )

    assert (
        statistics.rejected_examples
        == 1
    )

    assert (
        statistics.duplicate_examples
        == 1
    )

    assert (
        statistics.unique_examples
        == 3
    )

    assert (
        statistics.train_examples
        + statistics.validation_examples
        == 3
    )

    assert (
        statistics.minimum_formatted_characters
        > 0
    )

    assert (
        statistics.maximum_formatted_characters
        >= statistics.minimum_formatted_characters
    )

    assert (
        statistics.average_formatted_characters
        > 0
    )