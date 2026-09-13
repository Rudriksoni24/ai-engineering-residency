# Sprint 8 — Day 6 Report

## Title

Sprint 8 — Day 6: Data and Model Validation

## Artifact

Validation Suite

## Objective

Prevent invalid datasets and unacceptable candidate models from progressing through the ML lifecycle.

## Validation Architecture

Two independent validation layers are implemented:

Data Validation

and

Model Validation

Both return a shared structured ValidationResult.

## ValidationResult

The validation contract contains:

- passed
- checks
- failures
- metrics

Each ValidationCheck contains:

- name
- passed
- message
- observed
- expected

## Data Validation

The data validator checks:

- dataset is not empty
- required columns exist
- minimum dataset size
- target missing values
- feature missing fraction
- transaction amount range
- account age range
- transaction hour range
- country risk domain
- previous transaction count range
- account balance range
- fraud label domain
- both fraud classes exist
- transaction-type categories
- merchant categories
- duplicate-row fraction
- fraud-class distribution

## Data Validation Policy

Minimum rows:

500

Maximum feature missing fraction:

5%

Maximum duplicate fraction:

1%

Fraud-rate range:

1% to 30%

These thresholds are intentionally broad enough to detect malformed data without requiring byte-identical datasets.

## Model Validation

The candidate validator checks:

- model can predict
- model exposes probability predictions
- prediction shape
- binary prediction domain
- finite metrics
- minimum accuracy
- minimum precision
- minimum recall
- minimum F1
- minimum ROC-AUC
- minimum Average Precision
- candidate vs baseline regression

## Model Validation Policy

Minimum accuracy:

0.50

Minimum precision:

0.08

Minimum recall:

0.25

Minimum F1:

0.12

Minimum ROC-AUC:

0.60

Minimum Average Precision:

0.12

Maximum tolerated Average Precision regression:

0.02

## Baseline Comparison

The Day 1 raw-feature Logistic Regression model is trained on the same deterministic split.

Its Average Precision is used as a baseline.

The registered candidate must not regress from baseline Average Precision by more than the configured tolerance.

## Candidate

Registered model:

`Sprint08FraudDetectionModel`

Candidate version:

`1`

Source run ID:

`b7e13a823db24bd087758527829c773e`

## Data Validation Result

Status:

**PASS** (all 17 checks passed)

Fraud rate:

`0.0758` (7.58%)

Duplicate fraction:

`0.0` (0%)

Maximum missing fraction:

`0.0` (0%)

Additional metric recorded:

Row count: `5000`

## Baseline

Average Precision:

`0.2032`

## Candidate Metrics

Accuracy:

`0.7340`

Precision:

`0.1747`

Recall:

`0.6711`

F1:

`0.2772`

ROC-AUC:

`0.7422`

Average Precision:

`0.2254`

## Model Validation Result

Status:

**PASS** (all 11 checks passed, including `candidate_vs_baseline`)

The candidate's Average Precision (`0.2254`) is actually **higher** than the Day 1 raw-feature baseline (`0.2032`) — a regression check here isn't just satisfying a threshold, the candidate genuinely improved over baseline by roughly 0.022 (about 11% relative). This is a stronger result than "passed by staying within tolerance"; the feature-engineered pipeline from Day 4 is outperforming the simpler Day 1 baseline it's being compared against, not just avoiding regression from it.

## Lifecycle Decision

validation_status:

`passed`

promotion_eligible:

`True`

Passing Day 6 validation means the candidate is technically eligible for lifecycle promotion.

It does not imply production deployment.

## Design Separation

Day 4:
experiment tracking

Day 5:
registry and model versioning

Day 6:
data and model validation

Day 7:
full platform integration

## Limitations

Day 6 does not implement:

- production deployment
- automatic champion promotion
- monitoring
- drift detection
- calibration
- fairness analysis
- adversarial testing
- streaming validation
- Kubernetes
- CI/CD

## Validation Commands

Focused:
```bash
uv run pytest ml/tests/test_day06_validation.py -v
```

Sprint package:
```bash
uv run pytest ml/tests -v
```

Full repository:
```bash
uv run pytest -v
```

Ruff:
```bash
uv run ruff check ml
```

Demo:
```bash
uv run python -m ml.scripts.run_day06
```

## Result

Day 6 is complete: valid data passed all 17 checks; the registered candidate (`Sprint08FraudDetectionModel`, version `1`, sourced from run `b7e13a823db24bd087758527829c773e`) passed all 11 model validation checks, including a genuine improvement over baseline rather than a marginal pass; `validation_status` was updated to `passed` and `promotion_eligible` was set to `True`.

Worth carrying into Day 7: this run confirms the full Day 4 → Day 5 → Day 6 chain is now working consistently end to end using the same underlying run (`b7e13a823db24bd087758527829c773e`) and the same metrics throughout — no drift between what was tracked, what was registered, and what was validated. That consistency was not guaranteed a few days ago (see the Day 5 report for the MLflow 3.x model-URI fix that was required to get registry loading working at all); today's clean pass across every layer is a good signal that fix is holding up under real use, not just in isolated tests.