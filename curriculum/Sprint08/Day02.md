# Sprint 8 — Day 2: Feature Engineering

Artifact: Feature Engineering Lab

## Goal

Build reusable and leakage-safe feature transformations for structured
machine-learning data.

Compare:

baseline raw features

vs

engineered features

without claiming an improvement unless the resulting metrics demonstrate one.

## 1. Raw Features

Raw features come directly from the source dataset.

Examples:

- transaction_amount
- transaction_type
- account_age_days
- transaction_hour
- merchant_category
- country_risk
- previous_transaction_count
- account_balance

Raw does not necessarily mean suitable for direct model consumption.

## 2. Derived Features

Derived features are created from one or more raw values.

Examples used today:

- amount_log
- is_night_transaction
- amount_to_balance_ratio
- account_age_bucket
- transaction_velocity
- high_risk_category

The goal is to express useful structure more directly to the model.

## 3. Numerical Features

Numerical features represent measurable quantities.

Examples:

- transaction_amount
- account_age_days
- account_balance
- amount_log
- amount_to_balance_ratio

Numerical values often require:

- missing-value handling
- scaling
- clipping or transformation

## 4. Categorical Features

Categorical variables represent discrete groups.

Examples:

- transaction_type
- merchant_category
- account_age_bucket

Models such as Logistic Regression cannot directly consume strings.

They must be encoded.

Day 2 uses OneHotEncoder.

## 5. Missing Values

Real-world data frequently contains missing values.

Strategies include:

Numeric:
- median
- mean
- constant

Categorical:
- most-frequent
- explicit missing category

Today:

numeric -> median
categorical -> most-frequent

These statistics must be learned from training data only.

## 6. Scaling

Features can have very different magnitudes.

Example:

country_risk:
0 or 1

account_balance:
potentially thousands

StandardScaler transforms numeric features using:

z = (x - mean) / standard_deviation

The mean and standard deviation must come only from training data.

## 7. Encoding

One-hot encoding transforms a category such as:

transaction_type = transfer

into indicator columns such as:

transaction_type_card
transaction_type_transfer
transaction_type_cash_withdrawal

The encoder must tolerate categories not present during training.

Therefore:

handle_unknown="ignore"

is important.

## 8. Transformations

Some numeric features have skewed distributions.

Transaction amount is often strongly right-skewed.

A useful transformation is:

amount_log = log(1 + transaction_amount)

This compresses extreme values while preserving ordering.

## 9. Feature Interactions

Sometimes the relationship between multiple features is more useful than
either field independently.

Example:

amount_to_balance_ratio =
transaction_amount / account_balance

A 500-unit transaction may be normal for an account with a large balance but
unusual for an account with a small balance.

## 10. Leakage

Feature engineering can create leakage.

Bad example:

transaction_velocity =
number of all transactions belonging to this account over the entire dataset

If future transactions are included, the feature contains information from
after the prediction point.

Today we use only row-local or already-existing values.

Later systems must apply temporal cutoff rules to history-based features.

## 11. Fit vs Transform

Some feature transformations are stateless.

Example:

log(amount)

No statistics are learned.

Other transformations are stateful.

Examples:

- imputation
- scaling
- category vocabularies

Stateful transformations must:

fit(X_train)

then:

transform(X_train)
transform(X_test)

Never:

fit(X_test)

## 12. ColumnTransformer

ColumnTransformer allows different preprocessing strategies for different
column groups.

Example:

numerical columns:
imputation -> scaling

categorical columns:
imputation -> one-hot encoding

This creates one reproducible preprocessing graph.

## 13. Pipeline

Pipeline chains transformations and estimation.

Engineered pipeline:

raw input
    |
    v
feature builder
    |
    v
ColumnTransformer
    |
    v
LogisticRegression

The model therefore accepts the same raw transaction structure at training
and inference time.

## 14. Feature Engineering vs Preprocessing

Preprocessing changes representation primarily so the estimator can consume
the data.

Examples:

- scaling
- encoding
- imputation

Feature engineering attempts to expose new predictive relationships.

Examples:

- amount_to_balance_ratio
- night transaction flag
- account age bucket

The boundary is not always absolute, but the distinction is useful.

## 15. Comparison Principle

Day 2 compares:

baseline raw-feature model

vs

engineered-feature model

using:

- the same source dataset
- the same train/test split
- the same seed
- the same estimator family
- the same metrics

Otherwise the comparison is not meaningful.

## Day 2 Boundary

Implemented today:

- reusable feature builder
- deterministic feature transformations
- missing-value handling
- numeric scaling
- categorical encoding
- stable feature schema
- baseline vs engineered comparison

Not implemented today:

- Random Forest comparison
- gradient boosting
- class weighting experiments
- threshold tuning
- ROC-AUC comparison
- PR-AUC comparison
- MLflow
- registry
- deployment