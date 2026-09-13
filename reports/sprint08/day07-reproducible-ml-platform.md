# Sprint 8 — Day 7 Report

## Title

Sprint 8 — Day 7: Sprint Integration

## Artifact

Reproducible ML Platform

## Objective

Integrate Sprint 8 Days 1–6 into one coherent and reproducible local ML platform.

## Integrated Workflow

Raw Data
    ↓
Data Validation
    ↓
Dataset Fingerprint
    ↓
Deterministic Train/Test Split
    ↓
Feature Engineering
    ↓
Multiple Model Training
    ↓
Evaluation
    ↓
MLflow Tracking
    ↓
Candidate Selection
    ↓
Model Validation
    ↓
Model Registry
    ↓
Version / Lifecycle Alias

## Configuration

Random seed:

42

Dataset size:

5000

Test fraction:

0.20

MLflow experiment:

Sprint08-Reproducible-Platform

Registered model:

Sprint08FraudDetectionModel

## Dataset

Dataset fingerprint:

`3ecba3895569060b1a25418d1cac3171b782fd2554f0275d759990c7b013c354`

Fraud rate:

`0.0758` (7.58% — carried over from the Day 6 run against this same dataset fingerprint; Day 7's own console output doesn't re-print fraud rate directly, but the identical fingerprint confirms it's the same underlying data)

Data validation:

**PASS** (`Data validation: True`)

## Selected Model

Model:

`logistic_regression`

MLflow run ID:

`c3ba6711293748498ff6a25f1f72dc86`

MLflow model URI:

`models:/m-2cf6cce42fb24401804f65ca153407d7`

## Parameters

| Parameter | Value |
|---|---|
| categorical_encoder | OneHotEncoder |
| categorical_imputer | most_frequent |
| classifier__C | 1.0 |
| classifier__class_weight | balanced |
| classifier__dual | False |
| classifier__fit_intercept | True |
| classifier__intercept_scaling | 1 |
| classifier__l1_ratio | 0.0 |
| classifier__max_iter | 1000 |
| classifier__n_jobs | None |
| classifier__penalty | deprecated |
| classifier__random_state | 42 |
| classifier__solver | lbfgs |
| classifier__tol | 0.0001 |
| classifier__verbose | 0 |
| classifier__warm_start | False |
| dataset_fingerprint | 3ecba3895569060b1a25418d1cac3171b782fd2554f0275d759990c7b013c354 |
| feature_transformer | FraudFeatureTransformer |
| model_type | logistic_regression |
| numeric_imputer | median |
| numeric_scaler | StandardScaler |
| random_seed | 42 |
| test_size | 0.2 |
| threshold | 0.5 |

## Metrics

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

## Model Validation

Status:

**PASS**

Promotion eligible:

`True`

## Registry

Registered model:

Sprint08FraudDetectionModel

Version:

`2`

Registry URI:

`models:/Sprint08FraudDetectionModel/2`

Candidate alias:

candidate

Validated alias:

validated

## Reproducibility Verification

The platform was executed **twice in succession** using identical data generator, seed, dataset size, split configuration, feature configuration, and model configuration. Results below are the actual observed output from both runs, not a theoretical expectation:

| Field | Run 1 | Run 2 | Stable? |
|---|---|---|---|
| Dataset fingerprint | `3ecba3895...` | `3ecba3895...` | ✅ identical |
| Selected model | logistic_regression | logistic_regression | ✅ identical |
| Accuracy | 0.7340 | 0.7340 | ✅ identical |
| Precision | 0.1747 | 0.1747 | ✅ identical |
| Recall | 0.6711 | 0.6711 | ✅ identical |
| F1 | 0.2772 | 0.2772 | ✅ identical |
| ROC-AUC | 0.7422 | 0.7422 | ✅ identical |
| Average Precision | 0.2254 | 0.2254 | ✅ identical |
| Data/model validation | PASS / PASS | PASS / PASS | ✅ identical |
| MLflow run ID | `c3ba6711...` | `fa544bdf...` | ⚠️ changes (expected) |
| MLflow model URI | `models:/m-2cf6cce4...` | `models:/m-3a5892a3...` | ⚠️ changes (expected) |
| Registered version | `2` | `3` | ⚠️ changes (expected) |

This is exactly the expected reproducibility contract: **everything that reflects the data, the training procedure, and the result is bit-for-bit stable across runs; only the identifiers tied to a specific execution — run ID, model artifact ID, registry version number — change.** Each run is logged as its own distinct, independently auditable event (a fresh version registered each time), while the actual scientific result behind it is fully deterministic and reproducible from the same seed and dataset fingerprint.

## MLflow 3 Compatibility

The platform preserves the model URI returned directly by MLflow (`models:/m-...`) rather than reconstructing a legacy `runs:/.../model` URI anywhere downstream. This is a direct continuation of the fix made in Day 5 — see the Day 5 report for why the older `runs:/{run_id}/model` convention silently breaks under this MLflow version, and why the registry now reads the real model URI from a run tag instead of guessing at a path. Day 7's clean back-to-back runs, with the registry advancing to version 3 without any load or registration failures, confirm that fix holds up under repeated, independent executions — not just the single pass it was originally verified against.

## Result

Sprint integration is complete: deterministic data generation succeeded (identical fingerprint across both runs); data validation passed; experiment runs were tracked; multiple models were compared and logistic regression was selected consistently both times; model validation passed; candidate registration succeeded (versions 2 and 3, one per run); lifecycle aliases were assigned; and reproducibility was directly verified rather than assumed — two independent executions produced identical metrics, parameters, and dataset fingerprint while correctly generating distinct run IDs, model URIs, and registry versions for each execution.