# Sprint 8 — Day 6: Data and Model Validation

Artifact: Validation Suite

## Goal

Prevent invalid datasets and unacceptable models from advancing through the
machine-learning lifecycle.

## 1. Data Validation vs Model Validation

Data validation asks:

Is the dataset structurally and semantically acceptable?

Model validation asks:

Does the candidate model behave correctly and meet the required quality
thresholds?

These are separate concerns.

## 2. Structured Validation Result

Validation should not return only True or False.

A useful result contains:

- passed
- checks
- failures
- metrics

This allows callers to understand why validation passed or failed.

## 3. Validation Check

Each individual check records:

- name
- passed
- message
- observed value
- expected value

Example:

name:
transaction_hour_range

passed:
false

observed:
27

expected:
0 <= hour <= 23

## 4. Required Columns

The fraud dataset requires:

- transaction_amount
- transaction_type
- account_age_days
- transaction_hour
- merchant_category
- country_risk
- previous_transaction_count
- account_balance
- fraud_label

Missing required columns must fail validation.

## 5. Empty Dataset

An empty dataset cannot be used for training.

Validation must fail before model code executes.

## 6. Dataset Size

Very small datasets may technically train but produce meaningless evaluation.

Day 6 therefore defines a configurable minimum dataset size.

The threshold is intentionally realistic rather than arbitrarily large.

## 7. Missing Values

Missing feature values can sometimes be handled by preprocessing.

Validation should nevertheless measure missingness explicitly.

A policy determines the maximum acceptable missing fraction.

Target labels must not be missing.

## 8. Numeric Ranges

Examples:

transaction_amount >= 0

account_age_days >= 0

0 <= transaction_hour <= 23

country_risk in {0, 1}

previous_transaction_count >= 0

account_balance >= 0

Invalid values indicate malformed or semantically impossible input.

## 9. Label Validity

fraud_label must contain only:

0
1

Both classes must be present.

A dataset containing only legitimate transactions cannot meaningfully train
or evaluate fraud classification.

## 10. Categorical Validity

Expected transaction types:

- card
- transfer
- cash_withdrawal
- bill_payment

Expected merchant categories:

- grocery
- electronics
- travel
- fuel
- utilities
- other

Unexpected categories should fail strict validation for the current synthetic
dataset contract.

Production systems may choose different unknown-category policies.

## 11. Duplicate Rows

Duplicate records may distort training and evaluation.

Day 6 measures duplicate fraction and rejects datasets exceeding a configured
limit.

## 12. Class Distribution

Fraud should remain a minority class but must be represented.

The validation policy checks a reasonable fraud-rate range.

This detects failures such as:

- no fraud examples
- accidentally inverted labels
- corrupted generation logic

## 13. Model Prediction Validation

A candidate model must:

- support prediction
- return the expected number of predictions
- return valid binary classes
- produce probability scores
- produce finite metrics

A model that cannot predict correctly should fail before metric thresholds are
considered.

## 14. Metric Validation

Day 6 checks fraud-sensitive metrics including:

- precision
- recall
- F1
- ROC-AUC
- Average Precision

Thresholds should represent minimum acceptable quality, not artificially high
numbers chosen to force failure.

## 15. Candidate vs Baseline

A candidate should not silently regress far below an established baseline.

Day 6 therefore supports baseline comparison.

Example:

candidate Average Precision
must not fall materially below
baseline Average Precision

A small configurable tolerance is allowed.

## 16. Promotion Eligibility

Passing validation means:

eligible for lifecycle promotion

It does not mean:

deployed to production

Deployment remains outside Sprint 8.

## 17. Validation Status

The registered candidate can be tagged:

validation_status=passed

or:

validation_status=failed

The candidate alias itself remains unchanged.

## 18. Day 6 Boundary

Implemented today:

- structured validation contracts
- data validation
- schema checks
- missing-value checks
- numeric-range checks
- label validation
- categorical validation
- duplicate detection
- dataset-size validation
- class-distribution validation
- prediction validation
- metric validation
- candidate-vs-baseline comparison
- promotion eligibility
- registry validation status

Not implemented today:

- deployment
- Kubernetes
- CI/CD
- monitoring
- drift detection
- streaming validation
- final Sprint integration