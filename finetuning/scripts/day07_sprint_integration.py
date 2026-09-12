from __future__ import annotations

import gc
from pathlib import Path

import torch

from finetuning.data.pipeline import (
    DatasetPipeline,
    InstructionExample,
    PipelineConfig,
    format_instruction_example,
    format_instruction_prompt,
)
from finetuning.evaluation.comparison import (
    EvaluationCase,
    EvaluationResult,
    completion_loss,
    summarize_results,
)
from finetuning.training.config import (
    LocalLoRAConfig,
)
from finetuning.training.peft_local import (
    apply_lora,
    count_parameters,
    generate_text,
    load_base_model,
    load_saved_adapter,
    load_tokenizer,
    save_adapter,
    select_device,
    set_seed,
    train_adapter,
)

RAW_DOMAIN_EXAMPLES = [
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
            "Classify the transaction status."
        ),
        "input": (
            "Transaction TXN-1004 "
            "was approved."
        ),
        "response": (
            '{"transaction_id":"TXN-1004",'
            '"status":"APPROVED"}'
        ),
    },
    {
        "instruction": (
            "Classify the transaction status."
        ),
        "input": (
            "Transaction TXN-1005 "
            "was declined."
        ),
        "response": (
            '{"transaction_id":"TXN-1005",'
            '"status":"DECLINED"}'
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
            "Classify account review status."
        ),
        "input": (
            "Account ACC-5003 passed "
            "manual verification."
        ),
        "response": (
            '{"account_id":"ACC-5003",'
            '"review_status":"VERIFIED"}'
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
    {
        "instruction": (
            "Determine the transfer status."
        ),
        "input": (
            "Transfer TRF-7003 completed "
            "successfully."
        ),
        "response": (
            '{"transfer_id":"TRF-7003",'
            '"status":"COMPLETED"}'
        ),
    },
    {
        "instruction": (
            "Determine the transfer status."
        ),
        "input": (
            "Transfer TRF-7004 is still "
            "being processed."
        ),
        "response": (
            '{"transfer_id":"TRF-7004",'
            '"status":"PENDING"}'
        ),
    },

    # Deliberate normalized duplicate.
    {
        "instruction": (
            "  Classify the transaction status. "
        ),
        "input": (
            " Transaction TXN-1002 "
            "was   declined. "
        ),
        "response": (
            ' {"transaction_id":"TXN-1002",'
            '"status":"DECLINED"} '
        ),
    },

    # Deliberately malformed.
    {
        "instruction": (
            "Classify malformed record."
        ),
        "input": "Missing response.",
        "response": " ",
    },
]


SYSTEM_PROMPT = (
    "You are a banking operations assistant. "
    "Return only the requested JSON structure."
)


def build_training_text(
    example: InstructionExample,
) -> str:
    return format_instruction_example(
        example,
        system_prompt=SYSTEM_PROMPT,
    )


def build_evaluation_case(
    example: InstructionExample,
) -> EvaluationCase:
    return EvaluationCase(
        case_id=(
            example.example_id[:12]
        ),
        prompt=format_instruction_prompt(
            example,
            system_prompt=SYSTEM_PROMPT,
        ),
        expected_response=(
            example.response
        ),
    )


def release_models(
    *models: object,
) -> None:
    for model in models:
        del model

    gc.collect()

    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


def main() -> None:
    print("=" * 76)
    print(
        "Sprint 7 — Day 7: Sprint Integration"
    )
    print(
        "Artifact: Domain-Adapted Local Model"
    )
    print("=" * 76)

    training_config = LocalLoRAConfig(
        rank=4,
        alpha=8,
        dropout=0.05,
        target_modules=(
            "q_proj",
            "v_proj",
        ),
        learning_rate=5e-4,
        training_steps=30,
        max_length=192,
        seed=42,
        output_dir=Path(
            "artifacts/sprint07/"
            "day07-domain-adapter"
        ),
    )

    data_config = PipelineConfig(
        validation_ratio=0.25,
        seed=training_config.seed,
        system_prompt=SYSTEM_PROMPT,
    )

    set_seed(
        training_config.seed
    )

    device = select_device()

    print("\n1. Workload declaration")

    print(
        f"Base model:       "
        f"{training_config.model_name}"
    )

    print(
        f"Device:           "
        f"{device}"
    )

    print(
        f"LoRA rank:        "
        f"{training_config.rank}"
    )

    print(
        f"LoRA alpha:       "
        f"{training_config.alpha}"
    )

    print(
        f"LoRA dropout:     "
        f"{training_config.dropout}"
    )

    print(
        f"Targets:          "
        f"{training_config.target_modules}"
    )

    print(
        f"Learning rate:    "
        f"{training_config.learning_rate}"
    )

    print(
        f"Training steps:   "
        f"{training_config.training_steps}"
    )

    print(
        f"Maximum length:   "
        f"{training_config.max_length}"
    )

    print(
        f"Seed:             "
        f"{training_config.seed}"
    )

    print(
        f"Adapter artifact: "
        f"{training_config.output_dir}"
    )

    print(
        "Classification: "
        "real local small-model PEFT training"
    )

    print(
        "Production scale: NO"
    )

    print("\n2. Prepare domain dataset")

    pipeline = DatasetPipeline(
        data_config
    )

    dataset = pipeline.process(
        RAW_DOMAIN_EXAMPLES
    )

    stats = dataset.statistics

    print(
        f"Raw:          {stats.raw_examples}"
    )

    print(
        "Valid before dedup: "
        f"{stats.valid_examples_before_deduplication}"
    )

    print(
        f"Rejected:     {stats.rejected_examples}"
    )

    print(
        f"Duplicates:   {stats.duplicate_examples}"
    )

    print(
        f"Unique:       {stats.unique_examples}"
    )

    print(
        f"Train:        {stats.train_examples}"
    )

    print(
        f"Validation:   {stats.validation_examples}"
    )

    print("\nRejected examples:")

    for rejected in dataset.rejected:
        print(
            f"  index={rejected.index} "
            f"reason={rejected.reason}"
        )

    training_texts = [
        build_training_text(
            example
        )
        for example in dataset.split.train
    ]

    evaluation_cases = [
        build_evaluation_case(
            example
        )
        for example in dataset.split.validation
    ]

    print(
        "\n3. Load tokenizer and base model"
    )

    tokenizer = load_tokenizer(
        training_config.model_name
    )

    base_model = load_base_model(
        training_config.model_name
    )

    base_model.to(
        device
    )

    base_summary = count_parameters(
        base_model
    )

    print(
        "Base parameters: "
        f"{base_summary.total_parameters:,}"
    )

    print(
        "\n4. Base-model held-out evaluation"
    )

    base_losses: dict[
        str,
        float
    ] = {}

    base_generations: dict[
        str,
        str
    ] = {}

    for case in evaluation_cases:
        case.validate()

        loss = completion_loss(
            model=base_model,
            tokenizer=tokenizer,
            prompt=case.prompt,
            expected_response=(
                case.expected_response
            ),
            max_length=(
                training_config.max_length
            ),
            device=device,
        )

        base_losses[
            case.case_id
        ] = loss

        generation = generate_text(
            model=base_model,
            tokenizer=tokenizer,
            prompt=case.prompt,
            device=device,
            max_new_tokens=50,
        )

        base_generations[
            case.case_id
        ] = generation

        print(
            f"{case.case_id}: "
            f"base_loss={loss:.6f}"
        )

    print("\n5. Inject LoRA adapter")

    adapted_model = apply_lora(
        base_model,
        training_config,
    )

    adapted_model.to(
        device
    )

    adapted_summary = count_parameters(
        adapted_model
    )

    print(
        "Total parameters:     "
        f"{adapted_summary.total_parameters:,}"
    )

    print(
        "Trainable parameters: "
        f"{adapted_summary.trainable_parameters:,}"
    )

    print(
        "Frozen parameters:    "
        f"{adapted_summary.frozen_parameters:,}"
    )

    print(
        "Trainable percentage: "
        f"{adapted_summary.trainable_percentage:.4f}%"
    )

    adapted_model.print_trainable_parameters()

    print("\n6. Train domain adapter")

    metrics = train_adapter(
        model=adapted_model,
        tokenizer=tokenizer,
        training_texts=training_texts,
        config=training_config,
        device=device,
    )

    print(
        f"First training loss: "
        f"{metrics.first_loss:.6f}"
    )

    print(
        f"Final training loss: "
        f"{metrics.final_loss:.6f}"
    )

    print(
        "Training loss decreased: "
        f"{metrics.final_loss < metrics.first_loss}"
    )

    print("\n7. Save adapter")

    save_adapter(
        adapted_model,
        training_config.output_dir,
    )

    print(
        f"Saved: "
        f"{training_config.output_dir}"
    )

    print(
        "\n8. Release trained model "
        "and reload fresh base + adapter"
    )

    del adapted_model
    del base_model

    gc.collect()

    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    reloaded_model = (
        load_saved_adapter(
            model_name=(
                training_config.model_name
            ),
            adapter_dir=(
                training_config.output_dir
            ),
            device=device,
        )
    )

    print(
        "\n9. Adapted held-out evaluation"
    )

    results: list[
        EvaluationResult
    ] = []

    adapted_generations: dict[
        str,
        str
    ] = {}

    for case in evaluation_cases:
        adapted_loss = completion_loss(
            model=reloaded_model,
            tokenizer=tokenizer,
            prompt=case.prompt,
            expected_response=(
                case.expected_response
            ),
            max_length=(
                training_config.max_length
            ),
            device=device,
        )

        result = EvaluationResult(
            case_id=case.case_id,
            base_loss=(
                base_losses[
                    case.case_id
                ]
            ),
            adapted_loss=(
                adapted_loss
            ),
        )

        results.append(
            result
        )

        generation = generate_text(
            model=reloaded_model,
            tokenizer=tokenizer,
            prompt=case.prompt,
            device=device,
            max_new_tokens=50,
        )

        adapted_generations[
            case.case_id
        ] = generation

        print(
            f"{case.case_id}: "
            f"base={result.base_loss:.6f} "
            f"adapted={result.adapted_loss:.6f} "
            f"delta={result.loss_delta:+.6f} "
            f"improved={result.improved}"
        )

    print("\n10. Evaluation summary")

    summary = summarize_results(
        results
    )

    print(
        f"Cases:             "
        f"{summary.case_count}"
    )

    print(
        f"Improved cases:    "
        f"{summary.improved_cases}"
    )

    print(
        f"Regressed cases:   "
        f"{summary.regressed_cases}"
    )

    print(
        f"Unchanged cases:   "
        f"{summary.unchanged_cases}"
    )

    print(
        f"Average base loss: "
        f"{summary.average_base_loss:.6f}"
    )

    print(
        "Average adapted loss: "
        f"{summary.average_adapted_loss:.6f}"
    )

    print(
        f"Average delta:     "
        f"{summary.average_loss_delta:+.6f}"
    )

    print(
        f"Overall improved:  "
        f"{summary.improved_overall}"
    )

    print(
        "\n11. Qualitative before/after"
    )

    for case in evaluation_cases:
        print(
            "\n"
            + "-" * 72
        )

        print(
            f"CASE: {case.case_id}"
        )

        print(
            "\nEXPECTED:"
        )

        print(
            case.expected_response
        )

        print(
            "\nBASE:"
        )

        print(
            base_generations[
                case.case_id
            ]
        )

        print(
            "\nADAPTED:"
        )

        print(
            adapted_generations[
                case.case_id
            ]
        )

    print(
        "\n12. Evidence-based conclusion"
    )

    if summary.improved_overall:
        print(
            "The adapted model achieved lower "
            "average held-out completion loss."
        )

        print(
            "This supports improvement on this "
            "small deterministic evaluation set."
        )
    else:
        print(
            "The adapted model did not achieve "
            "lower average held-out completion loss."
        )

        print(
            "Do not claim domain improvement from "
            "this training run."
        )

    print(
        "\nThis result does NOT prove broad "
        "production-level improvement."
    )

    print(
        "\n13. RAG vs LoRA vs Hybrid"
    )

    print(
        """
RAG
----
Best fit:
- changing facts
- document knowledge
- traceable sources
- large knowledge stores

LoRA
----
Best fit:
- behavior
- style
- output structure
- terminology
- repeated task conventions

RAG + LoRA
----------
LoRA controls behavior.
RAG supplies current external knowledge.
"""
    )

    print(
        "\nSprint 7 integration run complete."
    )


if __name__ == "__main__":
    main()

    #uv run python -m finetuning.scripts.day07_sprint_integration