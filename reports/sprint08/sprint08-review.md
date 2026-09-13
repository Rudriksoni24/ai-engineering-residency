# Sprint 8 Review — Traditional ML and MLflow

## Target

Build reproducible ML training and experiment tracking systems.

## Day 1 — Classical ML Pipeline

Artifact:

ML Pipeline

Implemented:

- deterministic synthetic dataset
- train/test split
- preprocessing
- Logistic Regression baseline
- classification metrics

## Day 2 — Feature Engineering

Artifact:

Feature Engineering Lab

Implemented:

- reusable feature transformer
- derived fraud features
- leakage-safe preprocessing
- baseline vs engineered comparison

## Day 3 — Fraud Detection Modeling

Artifact:

Fraud Detection Model

Implemented:

- model comparison
- class imbalance handling
- threshold analysis
- ROC-AUC
- Average Precision
- candidate selection

Observed Day 3 candidate:

Logistic Regression

Observed tuned threshold:

0.4272

Observed metrics:

Accuracy: 0.5780
Precision: 0.1303
Recall: 0.8026
F1: 0.2243
ROC-AUC: 0.7422
Average Precision: 0.2254

## Day 4 — Experiment Tracking with MLflow

Artifact:

MLflow Tracking System

Implemented:

- local MLflow tracking
- run IDs
- parameters
- metrics
- tags
- artifacts
- dataset fingerprints
- parent/child runs
- model logging
- experiment comparison

MLflow 3 compatibility:

Model URIs returned directly by mlflow.sklearn.log_model() are preserved.

## Day 5 — Model Registry

Artifact:

Model Lifecycle Pipeline

Implemented:

- registered models
- model versions
- aliases
- lifecycle tags
- registry loading
- source-run lineage

## Day 6 — Data and Model Validation

Artifact:

Validation Suite

Implemented:

- structured ValidationResult
- schema validation
- missing-value checks
- range checks
- label checks
- categorical checks
- duplicate checks
- class-distribution checks
- prediction validation
- metric validation
- baseline regression checks

## Day 7 — Sprint Integration

Artifact:

Reproducible ML Platform

Implemented:

- end-to-end orchestration
- deterministic data generation
- validation
- training
- tracking
- comparison
- candidate selection
- model validation
- registry
- versioning
- lifecycle aliases
- reproducibility verification

## Cross-Day Consistency Check

**Day 3's tuned decision threshold (0.4272) was not carried forward into the tracked pipeline used from Day 4 onward.** Every run logged in Days 4–7 records `threshold: 0.5` — the untouched default — rather than the 0.4272 value Day 3 arrived at through explicit threshold analysis.

The effect is visible directly in the metrics:

| Metric | Day 3 (threshold 0.4272) | Days 4–7 (threshold 0.5) |
|---|---:|---:|
| Accuracy | 0.5780 | 0.7340 |
| Precision | 0.1303 | 0.1747 |
| Recall | 0.8026 | 0.6711 |
| F1 | 0.2243 | 0.2772 |
| ROC-AUC | 0.7422 | 0.7422 |
| Average Precision | 0.2254 | 0.2254 |

ROC-AUC and Average Precision are identical across both, because they're ranking-based metrics that don't depend on where the decision threshold is set — the model's underlying probability ordering didn't change. But the moment those probabilities are converted into a hard fraud/not-fraud decision, the threshold choice matters a great deal: at 0.4272, the model catches 80% of actual fraud (recall); at the default 0.5 used throughout tracking, it catches only 67%. For a fraud detector, where missed fraud is typically far more costly than a false alarm, this is a meaningful regression that happened silently — not through any bug, but simply because the tuned threshold from Day 3's analysis was never wired into the pipeline that Days 4–7 built on top of.

This is worth resolving explicitly in a future sprint: either the tracked pipeline should adopt Day 3's tuned threshold as its default going forward, or there should be a documented reason 0.5 was kept instead (e.g., a deliberate choice to optimize for a different business trade-off). As it stands, it reads as an oversight rather than a decision.

## Sprint Exit Criteria

- [x] Build a complete ML pipeline.
- [x] Track experiments with MLflow.
- [x] Compare multiple experiments.
- [x] Register a model.
- [x] Version model artifacts.
- [x] Track parameters and metrics.
- [x] Build reproducible training runs.

## Key Engineering Lessons

1. Accuracy is insufficient for imbalanced fraud classification.

2. Feature engineering and preprocessing must remain leakage-safe.

3. Model probability ranking and business decision thresholds are separate.

4. Experiment tracking must capture both configuration and outcomes.

5. Dataset identity is part of reproducibility.

6. Experiment runs and registry versions serve different lifecycle purposes.

7. Registration does not imply validation.

8. Validation should return structured evidence rather than a boolean alone.

9. Reproducibility concerns scientific outputs, not database-generated IDs.

10. MLflow model URIs should be treated as opaque identifiers rather than reconstructed from implementation assumptions.

11. A tuned parameter (like Day 3's decision threshold) is only as valuable as the pipeline stage that carries it forward — analysis that doesn't propagate into the tracked/deployed configuration can silently regress without any test catching it, since threshold-independent metrics (ROC-AUC, Average Precision) will look unchanged even when threshold-dependent ones (recall, precision, accuracy) shift substantially.

## Sprint Status

Sprint 8 complete.