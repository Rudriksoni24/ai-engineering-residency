# Sprint 7 — Day 4 Report

## Title

Dataset Preparation for Fine-Tuning

## Artifact

Training Dataset Pipeline

## Objective

Build a deterministic instruction-training dataset pipeline that validates,
normalizes, deduplicates, splits, formats, and measures examples before
fine-tuning.

## Domain

Synthetic banking and enterprise operations examples.

No real customer, financial, account, or production data is used.

## Pipeline

```text
Raw Examples
     ↓
Validation
     ↓
Normalization
     ↓
Deduplication
     ↓
Unique Examples
     ↓
Deterministic Split
     ↓
Leakage Validation
     ↓
Formatting
     ↓
Statistics
```

## Implemented

- instruction / input / response schema
- required-field validation
- empty instruction rejection
- empty response rejection
- type validation
- whitespace normalization
- optional input support
- canonical example representation
- deterministic SHA-256 example IDs
- normalized duplicate removal
- deterministic seeded train/validation splitting
- exact normalized leakage detection
- instruction-style formatting
- system/user/assistant message formatting
- dataset statistics
- rejected-example reporting

## Validation Behavior

Valid examples are normalized and accepted.

Malformed examples are recorded as rejected examples instead of silently
entering the training dataset.

## Deduplication

Duplicate identity is derived from normalized:

```text
instruction
input
response
```

This prevents superficial whitespace differences from bypassing exact
duplicate detection.

## Reproducibility

The split uses an isolated seeded random generator.

Given the same:

```text
dataset
seed
validation ratio
```

the same split is produced.

## Leakage Prevention

The pipeline verifies:

```text
train example IDs
∩
validation example IDs
=
empty set
```

This protects against normalized exact duplicate leakage.

It does not detect all semantic leakage.

## Formatting

Two representations are supported:

1. Canonical instruction format.
2. Chat-style system/user/assistant format.

The underlying structured example remains the source of truth.

## Statistics

The pipeline reports:

- raw count
- valid count before deduplication
- rejected count
- duplicate count
- unique count
- train count
- validation count
- minimum formatted character length
- maximum formatted character length
- average formatted character length

## Sequence Length

Today's core statistics measure characters, not tokenizer tokens.

Token counts depend on the selected model tokenizer.

Model-aware tokenization and truncation should occur at the
training/integration boundary.

## Limitations

The pipeline currently does not detect:

- semantic duplicates
- paraphrase leakage
- entity-level leakage
- temporal leakage
- source-document leakage
- label imbalance
- toxicity or safety quality
- factual correctness
- tokenizer-specific sequence overflow

These require additional domain-aware policies.

## Training

No model training occurs on Day 4.

The artifact is the dataset pipeline.

## Validation

```bash
uv run pytest finetuning/tests/test_dataset_pipeline.py -v
```

```bash
uv run pytest finetuning/tests -v
```

```bash
uv run python finetuning/scripts/day04_dataset_pipeline.py
```

```bash
uv run ruff check finetuning
```

```bash
uv run pytest -v
```

## Sprint Exit Criterion Earned

After successful validation:

```text
Prepare instruction data.
```