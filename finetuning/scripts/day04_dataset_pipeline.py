from __future__ import annotations

import json

from finetuning.data.pipeline import (
    DatasetPipeline,
    PipelineConfig,
    format_chat_messages,
    format_instruction_example,
)

RAW_EXAMPLES = [
    {
        "instruction": (
            "Classify the transaction status."
        ),
        "input": (
            "Transaction TXN-1001 "
            "was approved."
        ),
        "response": (
            '{"transaction_id":"TXN-1001",'
            '"status":"APPROVED"}'
        ),
    },
    {
        "instruction": (
            "Classify the transaction status."
        ),
        "input": (
            "Transaction TXN-1002 "
            "was declined."
        ),
        "response": (
            '{"transaction_id":"TXN-1002",'
            '"status":"DECLINED"}'
        ),
    },
    {
        "instruction": (
            "Classify the transaction status."
        ),
        "input": (
            "Transaction TXN-1003 "
            "is pending."
        ),
        "response": (
            '{"transaction_id":"TXN-1003",'
            '"status":"PENDING"}'
        ),
    },
    {
        "instruction": (
            "Classify account review status."
        ),
        "input": (
            "Account ACC-5001 passed "
            "manual verification."
        ),
        "response": (
            '{"account_id":"ACC-5001",'
            '"review_status":"VERIFIED"}'
        ),
    },
    {
        "instruction": (
            "Classify account review status."
        ),
        "input": (
            "Account ACC-5002 requires "
            "additional documentation."
        ),
        "response": (
            '{"account_id":"ACC-5002",'
            '"review_status":"DOCUMENTS_REQUIRED"}'
        ),
    },
    {
        "instruction": (
            "Determine the transfer status."
        ),
        "input": (
            "Transfer TRF-7001 completed "
            "successfully."
        ),
        "response": (
            '{"transfer_id":"TRF-7001",'
            '"status":"COMPLETED"}'
        ),
    },
    {
        "instruction": (
            "Determine the transfer status."
        ),
        "input": (
            "Transfer TRF-7002 failed "
            "validation."
        ),
        "response": (
            '{"transfer_id":"TRF-7002",'
            '"status":"FAILED"}'
        ),
    },

    # Intentional duplicate after normalization.
    {
        "instruction": (
            "  Classify   the transaction status. "
        ),
        "input": (
            " Transaction TXN-1002   was declined. "
        ),
        "response": (
            ' {"transaction_id":"TXN-1002",'
            '"status":"DECLINED"} '
        ),
    },

    # Intentional malformed record.
    {
        "instruction": (
            "Classify malformed example."
        ),
        "input": "Missing output.",
        "response": "   ",
    },
]


def print_examples(
    title: str,
    examples: tuple,
) -> None:
    print(f"\n{title}")
    print("-" * len(title))

    for index, example in enumerate(
        examples,
        start=1,
    ):
        print(
            f"{index}. "
            f"{example.example_id[:12]} "
            f"{example.instruction}"
        )


def main() -> None:
    print("=" * 72)
    print(
        "Sprint 7 — Day 4: "
        "Dataset Preparation for Fine-Tuning"
    )
    print(
        "Artifact: Training Dataset Pipeline"
    )
    print("=" * 72)

    config = PipelineConfig(
        validation_ratio=0.25,
        seed=42,
        system_prompt=(
            "You are a banking operations assistant. "
            "Respond using the requested structured format."
        ),
    )

    pipeline = DatasetPipeline(
        config
    )

    print("\n1. Raw dataset")

    print(
        f"Raw records: "
        f"{len(RAW_EXAMPLES)}"
    )

    result = pipeline.process(
        RAW_EXAMPLES
    )

    print("\n2. Rejections")

    if not result.rejected:
        print("No rejected records.")
    else:
        for rejected in result.rejected:
            print(
                f"index={rejected.index} "
                f"reason={rejected.reason}"
            )

    print("\n3. Dataset statistics")

    stats = result.statistics

    print(
        f"Raw examples:                  "
        f"{stats.raw_examples}"
    )

    print(
        f"Valid before deduplication:    "
        f"{stats.valid_examples_before_deduplication}"
    )

    print(
        f"Rejected examples:             "
        f"{stats.rejected_examples}"
    )

    print(
        f"Duplicates removed:            "
        f"{stats.duplicate_examples}"
    )

    print(
        f"Unique examples:               "
        f"{stats.unique_examples}"
    )

    print(
        f"Training examples:             "
        f"{stats.train_examples}"
    )

    print(
        f"Validation examples:           "
        f"{stats.validation_examples}"
    )

    print(
        f"Minimum formatted characters:  "
        f"{stats.minimum_formatted_characters}"
    )

    print(
        f"Maximum formatted characters:  "
        f"{stats.maximum_formatted_characters}"
    )

    print(
        f"Average formatted characters:  "
        f"{stats.average_formatted_characters:.2f}"
    )

    print_examples(
        "4. Training split",
        result.split.train,
    )

    print_examples(
        "5. Validation split",
        result.split.validation,
    )

    example = result.split.train[0]

    print(
        "\n6. Canonical instruction format"
    )

    print(
        format_instruction_example(
            example,
            system_prompt=(
                config.system_prompt
            ),
        )
    )

    print(
        "\n7. Chat-style representation"
    )

    messages = format_chat_messages(
        example,
        system_prompt=(
            config.system_prompt
        ),
    )

    print(
        json.dumps(
            messages,
            indent=2,
            ensure_ascii=False,
        )
    )

    print(
        "\n8. Reproducibility check"
    )

    second_result = pipeline.process(
        RAW_EXAMPLES
    )

    same_train = (
        result.split.train
        == second_result.split.train
    )

    same_validation = (
        result.split.validation
        == second_result.split.validation
    )

    print(
        "Same train split:      "
        f"{same_train}"
    )

    print(
        "Same validation split: "
        f"{same_validation}"
    )

    print("\n9. Interpretation")

    print(
        "Malformed examples were rejected."
    )

    print(
        "Whitespace was normalized."
    )

    print(
        "Normalized duplicates were removed."
    )

    print(
        "The dataset was split deterministically."
    )

    print(
        "Train and validation examples "
        "have separate identities."
    )

    print(
        "Instruction and chat formats "
        "were generated consistently."
    )

    print(
        "No model training occurred."
    )

    print("\nDay 4 pipeline complete.")


if __name__ == "__main__":
    main()

    # uv run python -m finetuning.scripts.day04_dataset_pipeline