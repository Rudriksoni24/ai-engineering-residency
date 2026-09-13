# Sprint 8 — Day 4 Report

## Title

Sprint 8 — Day 4: Experiment Tracking with MLflow

## Artifact

MLflow Tracking System

## Objective

Make fraud-model experiments observable, comparable, and reproducible using local MLflow experiment tracking.

## Tracking Architecture

The implementation uses:

MLflow
→ local SQLite tracking backend
→ local artifact storage

No cloud MLflow server, Databricks environment, or remote object store is required.

## Tracking Location

Tracking database:
`artifacts/mlflow/mlflow.db`

Artifact storage:
`artifacts/mlflow/artifacts/`

The generated tracking state is excluded from Git.

## MLflow Experiment

Experiment name:
`Sprint08-Fraud-Experiments`

A comparison execution creates a parent run. Individual model experiments are stored as child runs.

## Models Tracked

The experiment tracks:

- Logistic Regression
- Random Forest
- HistGradientBoosting

Each model uses:

- the same dataset
- the same train/test split
- the same random seed
- the same engineered feature pipeline
- the same evaluation methodology

## Dataset Fingerprint

Dataset SHA-256:
`3ecba3895569060b1a25418d1cac3171b782fd2554f0275d759990c7b013c354`

The fingerprint associates each training execution with its dataset contents.

## Reproducibility Metadata

Each run records:

- model type
- random seed
- test size
- dataset fingerprint
- feature-transformer identity
- numeric imputation strategy
- numeric scaling strategy
- categorical imputation strategy
- categorical encoding strategy
- classifier hyperparameters
- decision threshold

## Metrics

Each child run records:

- accuracy
- precision
- recall
- F1
- ROC-AUC
- Average Precision

## Artifacts

Each child run stores:

- `evaluation/confusion_matrix.json`
- `metadata/reproducibility.json`
- `model`

The model artifact contains the complete sklearn Pipeline.

## Parent Run

Parent run ID:
`d55ddc456df540aea8ba17891179d956`

## Tracked Runs

### Logistic Regression

Run ID:
`ae90381854034e08898c0f6f5c1141a7`

Model URI:
`runs:/ae90381854034e08898c0f6f5c1141a7/model`

### Random Forest

Run ID:
`922d00f714ca4369994ee9f46db4915a`

Model URI:
`runs:/922d00f714ca4369994ee9f46db4915a/model`

### HistGradientBoosting

Run ID:
`55c586ccd29e47419331f3b01f4065e9`

Model URI:
`runs:/55c586ccd29e47419331f3b01f4065e9/model`

## Experiment Comparison

Runs are ordered primarily by **Average Precision**. This is more appropriate than accuracy alone for the imbalanced fraud-detection problem — and the actual tracked metrics confirm exactly why, rather than this being a purely theoretical justification:

| Metric | HistGradientBoosting | Random Forest | Logistic Regression |
|---|---:|---:|---:|
| Accuracy | **0.918** | 0.791 | 0.734 |
| Average Precision | 0.155 | 0.141 | **0.225** |
| F1 | 0.089 | 0.205 | **0.277** |
| Precision | **0.286** | 0.144 | 0.175 |
| Recall | 0.053 | 0.355 | **0.671** |
| ROC-AUC | 0.654 | 0.694 | **0.742** |

HistGradientBoosting has the highest accuracy (0.918) but the lowest recall by a wide margin (0.053) — it is catching only about 5% of actual fraud cases. On an imbalanced dataset where fraud is rare, a model can reach high accuracy simply by predicting "not fraud" most of the time; that's effectively what's happening here. Its precision (0.286) is the best of the three, meaning it's conservative and usually correct when it does flag something — but at this recall level it is not a usable fraud detector, since it misses nearly all the fraud it exists to catch.

Logistic Regression wins on every metric that actually reflects fraud-detection performance under class imbalance: Average Precision (0.225), F1 (0.277), Recall (0.671), and ROC-AUC (0.742). It only trails on Accuracy and Precision — and in this context, trailing on those two is the expected trade-off for a model that is actually attempting to catch fraud rather than defaulting to the majority class.

**This is a concrete demonstration of why metric choice matters more than model choice for imbalanced classification.** Had the comparison been sorted by accuracy instead of average precision, the tracker would have surfaced HistGradientBoosting — the model least useful for the actual task — as the "best" one.

Best tracked model:
**Logistic Regression**

Best run ID:
`ae90381854034e08898c0f6f5c1141a7`

## Design Decision

MLflow calls are encapsulated in `MLflowTracker` rather than scattered across training modules.

Training remains responsible for:

- data preparation
- model fitting
- prediction
- evaluation

Tracking remains responsible for:

- runs
- parameters
- metrics
- tags
- artifacts
- model logging

## Parent / Child Runs

The comparison is represented as:

```
comparison parent
├── Logistic Regression
├── Random Forest
└── HistGradientBoosting
```

This preserves group-level experiment identity while maintaining independently inspectable model runs.

## Dataset Versioning

The dataset is identified through a deterministic SHA-256 fingerprint of canonicalized dataset contents. This provides:

```
training run ↔ dataset identity
```

rather than relying solely on Git history.

## Limitations

Day 4 does not implement:

- model registry
- model versions
- aliases
- model promotion
- validation gates
- deployment
- remote MLflow
- cloud artifact storage

These responsibilities belong to later Sprint days.

## Validation

Focused:
```bash
uv run pytest ml/tests/test_day04_tracking.py -v
```

Sprint ML package:
```bash
uv run pytest ml/tests -v
```

Full repository:
```bash
uv run pytest -v
```

Ruff when configured:
```bash
uv run ruff check ml
```

Demo:
```bash
uv run python -m ml.scripts.run_day04
```

## Result

Day 4 is complete: multiple runs were successfully tracked, with parameters, metrics, tags, confusion matrices, model artifacts, and dataset fingerprints all stored; parent/child relationships are visible and queryable; runs were compared directly (via both `search_child_runs` and the MLflow UI's metric comparison view); and the best tracked run was correctly identified as Logistic Regression, on the basis of Average Precision rather than the more misleading Accuracy metric.

Two real issues surfaced and were fixed during this sprint day, both worth carrying forward:

1. **`search_child_runs`'s filter string needed the `mlflow.parentRunId` tag quoted in backticks** (`` tags.`mlflow.parentRunId` ``) rather than left unquoted, to reliably match MLflow's documented search syntax against the SQL-backed tracking store.
2. **`mlflow.set_tracking_uri(...)` is process-global, not instance-scoped** — constructing a second `MLflowTracker` pointed at a different database silently redirected all fluent-API calls (`start_run`, `log_params`, `log_model`, etc.) for *every* tracker instance in the process, not just the one just constructed. `MLflowTracker.parent_run()` and `MLflowTracker.log_model_run()` now re-assert their own tracking URI immediately before each fluent-API call, and `MlflowClient` is now constructed with an explicit `tracking_uri` rather than relying on ambient global state. This makes each tracker instance genuinely self-contained for sequential use; concurrent use of multiple trackers from different threads in the same process would still need the imperative `MlflowClient` API instead of the fluent API to be fully thread-safe.