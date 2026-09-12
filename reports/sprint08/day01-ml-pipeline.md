# Sprint 8 — Day 1 Report

## Title

Sprint 8 — Day 1: Classical ML Pipeline

## Artifact

ML Pipeline

## Objective

Build an end-to-end classical supervised learning pipeline from raw structured
data through deterministic training and evaluation.

## Implementation

The Day 1 implementation contains:

- deterministic synthetic banking transaction generation
- binary fraud target
- raw dataset validation
- train/test separation
- stratified splitting
- numerical preprocessing
- categorical preprocessing
- Logistic Regression baseline
- classification prediction
- accuracy measurement
- precision measurement
- recall measurement
- F1 measurement
- confusion matrix
- deterministic tests

## Architecture

Raw Synthetic Dataset
    |
    v
Basic Validation
    |
    v
Features / Target
    |
    v
Stratified Train/Test Split
    |
    v
ColumnTransformer
    |
    +-- numerical preprocessing
    |
    +-- categorical preprocessing
    |
    v
LogisticRegression
    |
    v
Predictions
    |
    v
Evaluation Metrics

## Reproducibility

Controlled variables:

- dataset random seed
- train/test random seed
- LogisticRegression random_state
- fixed test size
- deterministic dataset size

Repeated runs using the same configuration should produce the same
predictions and metrics.

## Leakage Protection

The raw dataset is split before the sklearn Pipeline is fitted.

Therefore preprocessing statistics are learned only from training data.

The target column is separated from model features.

## Metrics

The Day 1 demo reports:

- accuracy
- precision
- recall
- F1
- confusion matrix

Accuracy alone is not sufficient because fraud classification is imbalanced.

## Baseline Model

The baseline estimator is Logistic Regression.

No class weighting or threshold optimization is performed on Day 1.

These belong to later fraud-modeling work.

## Boundaries

Not implemented:

- engineered fraud features
- model comparison
- threshold tuning
- class-weight experiments
- MLflow
- registry
- promotion
- deployment

## Validation

Focused test command:

uv run pytest ml/tests -v

Full regression command:

uv run pytest -v

Ruff command when configured:

uv run ruff check ml

## Result

Day 1 is complete only after:

- focused tests pass
- full regression passes
- demo runs successfully
- repository contains no accidental generated artifacts