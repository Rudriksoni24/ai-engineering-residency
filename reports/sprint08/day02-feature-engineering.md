# Sprint 8 — Day 2 Report

## Title

Sprint 8 — Day 2: Feature Engineering

## Artifact

Feature Engineering Lab

## Objective

Build reusable, deterministic, and leakage-safe feature transformations for
the Sprint 8 structured fraud dataset.

## Features Added

The engineered pipeline adds:

- amount_log
- is_night_transaction
- amount_to_balance_ratio
- account_age_bucket
- transaction_velocity
- high_risk_category

## Design

Feature engineering is implemented as an sklearn-compatible transformer:

FraudFeatureTransformer

Architecture:

raw transaction
    |
    v
FraudFeatureTransformer
    |
    v
ColumnTransformer
    |
    +-- numerical imputation/scaling
    |
    +-- categorical imputation/encoding
    |
    v
LogisticRegression

## Leakage Protection

The train/test split occurs before estimator fitting.

Feature engineering uses only row-local information.

Training-derived preprocessing statistics are fitted only using training data.

The test suite verifies that scaler statistics do not change when predictions
are made against extreme test values.

## Missing Values

Numerical values:

median imputation

Categorical values:

most-frequent imputation

Undefined amount-to-balance ratios become missing values and are handled by
the numerical imputer.

## Categorical Features

Categorical values are encoded using:

OneHotEncoder(handle_unknown="ignore")

This allows inference to tolerate categories not seen during training.

## Comparison

Day 2 compares:

baseline raw features

vs

engineered features

using:

- the same dataset
- identical train/test split
- identical random seed
- identical Logistic Regression estimator family
- identical metric calculation

## Metrics

The comparison reports:

- accuracy
- precision
- recall
- F1
- confusion matrix

No improvement should be claimed unless observed metrics support the claim.

## Limitations

Current feature engineering does not implement:

- temporal feature windows
- historical account aggregation
- model comparison
- class weighting
- threshold optimization
- MLflow tracking
- model registry

## Validation

Focused:

uv run pytest ml/tests/test_day02_features.py -v

Sprint package:

uv run pytest ml/tests -v

Full repository:

uv run pytest -v

Ruff when configured:

uv run ruff check ml

## Result

Day 2 is complete only when:

- feature tests pass
- Day 1 tests still pass
- full repository tests pass
- comparison demo runs successfully
- generated metrics are reviewed without unsupported improvement claims