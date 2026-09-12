from __future__ import annotations

import hashlib
import json
import random
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from statistics import mean
from typing import Any

_WHITESPACE_PATTERN = re.compile(r"\s+")


@dataclass(frozen=True)
class PipelineConfig:
    validation_ratio: float = 0.2
    seed: int = 42

    system_prompt: str = (
        "You are a banking operations assistant."
    )

    def validate(self) -> None:
        if not 0.0 < self.validation_ratio < 1.0:
            raise ValueError(
                "validation_ratio must be between 0 and 1"
            )

        if not self.system_prompt.strip():
            raise ValueError(
                "system_prompt cannot be empty"
            )


@dataclass(frozen=True)
class InstructionExample:
    instruction: str
    input_text: str
    response: str

    @property
    def canonical_payload(self) -> str:
        payload = {
            "instruction": self.instruction,
            "input": self.input_text,
            "response": self.response,
        }

        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    @property
    def example_id(self) -> str:
        return hashlib.sha256(
            self.canonical_payload.encode(
                "utf-8"
            )
        ).hexdigest()


@dataclass(frozen=True)
class RejectedExample:
    index: int
    reason: str
    raw_example: Mapping[str, Any]


@dataclass(frozen=True)
class DatasetSplit:
    train: tuple[InstructionExample, ...]
    validation: tuple[InstructionExample, ...]


@dataclass(frozen=True)
class DatasetStatistics:
    raw_examples: int
    valid_examples_before_deduplication: int
    rejected_examples: int
    duplicate_examples: int
    unique_examples: int
    train_examples: int
    validation_examples: int
    minimum_formatted_characters: int
    maximum_formatted_characters: int
    average_formatted_characters: float


@dataclass(frozen=True)
class PipelineResult:
    examples: tuple[InstructionExample, ...]
    rejected: tuple[RejectedExample, ...]
    split: DatasetSplit
    statistics: DatasetStatistics


def normalize_text(
    value: str,
) -> str:
    """
    Normalize superficial whitespace without changing
    meaningful word content.
    """

    return _WHITESPACE_PATTERN.sub(
        " ",
        value.strip(),
    )


def validate_raw_example(
    raw_example: Mapping[str, Any],
) -> None:
    if "instruction" not in raw_example:
        raise ValueError(
            "missing required field: instruction"
        )

    if "response" not in raw_example:
        raise ValueError(
            "missing required field: response"
        )

    instruction = raw_example[
        "instruction"
    ]

    response = raw_example[
        "response"
    ]

    input_text = raw_example.get(
        "input",
        "",
    )

    if not isinstance(
        instruction,
        str,
    ):
        raise ValueError(  # noqa: TRY004
            "instruction must be a string"
        )

    if not isinstance(
        response,
        str,
    ):
        raise ValueError(  # noqa: TRY004
            "response must be a string"
        )

    if not isinstance(
        input_text,
        str,
    ):
        raise ValueError(  # noqa: TRY004
            "input must be a string"
        )

    if not normalize_text(
        instruction
    ):
        raise ValueError(
            "instruction cannot be empty"
        )

    if not normalize_text(
        response
    ):
        raise ValueError(
            "response cannot be empty"
        )


def normalize_example(
    raw_example: Mapping[str, Any],
) -> InstructionExample:
    validate_raw_example(
        raw_example
    )

    return InstructionExample(
        instruction=normalize_text(
            raw_example["instruction"]
        ),
        input_text=normalize_text(
            raw_example.get(
                "input",
                "",
            )
        ),
        response=normalize_text(
            raw_example["response"]
        ),
    )


def deduplicate_examples(
    examples: Sequence[InstructionExample],
) -> tuple[
    list[InstructionExample],
    int,
]:
    seen: set[str] = set()

    unique: list[
        InstructionExample
    ] = []

    duplicate_count = 0

    for example in examples:
        if example.example_id in seen:
            duplicate_count += 1
            continue

        seen.add(
            example.example_id
        )

        unique.append(
            example
        )

    return (
        unique,
        duplicate_count,
    )


def split_examples(
    examples: Sequence[InstructionExample],
    *,
    validation_ratio: float,
    seed: int,
) -> DatasetSplit:
    if not 0.0 < validation_ratio < 1.0:
        raise ValueError(
            "validation_ratio must be between 0 and 1"
        )

    if len(examples) < 2:
        raise ValueError(
            "at least two unique examples are required "
            "for train/validation splitting"
        )

    shuffled = list(
        examples
    )

    random_generator = random.Random(
        seed
    )

    random_generator.shuffle(
        shuffled
    )

    validation_count = round(
        len(shuffled)
        * validation_ratio
    )

    validation_count = max(
        1,
        validation_count,
    )

    validation_count = min(
        validation_count,
        len(shuffled) - 1,
    )

    validation = tuple(
        shuffled[:validation_count]
    )

    train = tuple(
        shuffled[validation_count:]
    )

    return DatasetSplit(
        train=train,
        validation=validation,
    )


def find_split_leakage(
    split: DatasetSplit,
) -> set[str]:
    train_ids = {
        example.example_id
        for example in split.train
    }

    validation_ids = {
        example.example_id
        for example in split.validation
    }

    return (
        train_ids
        & validation_ids
    )


def validate_no_split_leakage(
    split: DatasetSplit,
) -> None:
    leaked_ids = find_split_leakage(
        split
    )

    if leaked_ids:
        raise ValueError(
            "train/validation leakage detected: "
            f"{len(leaked_ids)} overlapping example(s)"
        )


def format_instruction_example(
    example: InstructionExample,
    *,
    system_prompt: str,
) -> str:
    sections = [
        "### System",
        normalize_text(
            system_prompt
        ),
        "",
        "### Instruction",
        example.instruction,
    ]

    if example.input_text:
        sections.extend(
            [
                "",
                "### Input",
                example.input_text,
            ]
        )

    sections.extend(
        [
            "",
            "### Response",
            example.response,
        ]
    )

    return "\n".join(
        sections
    )

def format_instruction_prompt(
    example: InstructionExample,
    *,
    system_prompt: str,
) -> str:
    sections = [
        "### System",
        normalize_text(
            system_prompt
        ),
        "",
        "### Instruction",
        example.instruction,
    ]

    if example.input_text:
        sections.extend(
            [
                "",
                "### Input",
                example.input_text,
            ]
        )

    sections.extend(
        [
            "",
            "### Response",
            "",
        ]
    )

    return "\n".join(
        sections
    )


def format_chat_messages(
    example: InstructionExample,
    *,
    system_prompt: str,
) -> list[dict[str, str]]:
    user_content = (
        example.instruction
    )

    if example.input_text:
        user_content = (
            f"{example.instruction}\n\n"
            f"Context:\n"
            f"{example.input_text}"
        )

    return [
        {
            "role": "system",
            "content": normalize_text(
                system_prompt
            ),
        },
        {
            "role": "user",
            "content": user_content,
        },
        {
            "role": "assistant",
            "content": example.response,
        },
    ]


def calculate_statistics(
    *,
    raw_count: int,
    valid_before_deduplication: int,
    rejected_count: int,
    duplicate_count: int,
    unique_examples: Sequence[
        InstructionExample
    ],
    split: DatasetSplit,
    system_prompt: str,
) -> DatasetStatistics:
    formatted_lengths = [
        len(
            format_instruction_example(
                example,
                system_prompt=system_prompt,
            )
        )
        for example in unique_examples
    ]

    if not formatted_lengths:
        raise ValueError(
            "cannot calculate statistics "
            "for an empty dataset"
        )

    return DatasetStatistics(
        raw_examples=raw_count,
        valid_examples_before_deduplication=(
            valid_before_deduplication
        ),
        rejected_examples=rejected_count,
        duplicate_examples=duplicate_count,
        unique_examples=len(
            unique_examples
        ),
        train_examples=len(
            split.train
        ),
        validation_examples=len(
            split.validation
        ),
        minimum_formatted_characters=min(
            formatted_lengths
        ),
        maximum_formatted_characters=max(
            formatted_lengths
        ),
        average_formatted_characters=mean(
            formatted_lengths
        ),
    )


class DatasetPipeline:
    def __init__(
        self,
        config: PipelineConfig,
    ) -> None:
        config.validate()

        self.config = config

    def process(
        self,
        raw_examples: Sequence[
            Mapping[str, Any]
        ],
    ) -> PipelineResult:
        if not raw_examples:
            raise ValueError(
                "raw_examples cannot be empty"
            )

        valid_examples: list[
            InstructionExample
        ] = []

        rejected: list[
            RejectedExample
        ] = []

        for index, raw_example in enumerate(
            raw_examples
        ):
            try:
                normalized = normalize_example(
                    raw_example
                )
            except ValueError as error:
                rejected.append(
                    RejectedExample(
                        index=index,
                        reason=str(error),
                        raw_example=raw_example,
                    )
                )

                continue

            valid_examples.append(
                normalized
            )

        unique_examples, duplicate_count = (
            deduplicate_examples(
                valid_examples
            )
        )

        if len(unique_examples) < 2:
            raise ValueError(
                "at least two valid unique examples "
                "are required after cleaning"
            )

        split = split_examples(
            unique_examples,
            validation_ratio=(
                self.config.validation_ratio
            ),
            seed=self.config.seed,
        )

        validate_no_split_leakage(
            split
        )

        statistics = calculate_statistics(
            raw_count=len(
                raw_examples
            ),
            valid_before_deduplication=len(
                valid_examples
            ),
            rejected_count=len(
                rejected
            ),
            duplicate_count=duplicate_count,
            unique_examples=unique_examples,
            split=split,
            system_prompt=(
                self.config.system_prompt
            ),
        )

        return PipelineResult(
            examples=tuple(
                unique_examples
            ),
            rejected=tuple(
                rejected
            ),
            split=split,
            statistics=statistics,
        )