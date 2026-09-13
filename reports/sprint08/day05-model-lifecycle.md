# Sprint 8 — Day 5 Report

## Title

Sprint 8 — Day 5: Model Registry

## Artifact

Model Lifecycle Pipeline

## Objective

Manage the selected fraud-model artifact through a versioned MLflow registry with aliases, lifecycle metadata, registry loading, and source-run lineage.

## Registry Backend

The Model Registry uses the existing local MLflow SQLite backend:

`artifacts/mlflow/mlflow.db`

Model artifacts remain in:

`artifacts/mlflow/artifacts/`

No remote registry or cloud dependency is required.

## Registered Model

Registered model name:

`Sprint08FraudDetectionModel`

## Selected Source Run

Run ID:

`b7e13a823db24bd087758527829c773e`

Model type:

`logistic_regression`

Average Precision:

`0.2254`

## Registered Version

Version:

`1`

Version URI:

`models:/Sprint08FraudDetectionModel/1`

## Candidate Alias

Alias:

`candidate`

Alias URI:

`models:/Sprint08FraudDetectionModel@candidate`

The alias points to the current Day 5 candidate version.

## Lifecycle Metadata

`lifecycle_status=candidate`

`validation_status=pending`

The candidate has not yet passed Day 6 validation.

## Source-Run Lineage

The registered version preserves its source run:

| Field | Value |
|---|---|
| model_name | `Sprint08FraudDetectionModel` |
| version | `1` |
| source_run_id | `b7e13a823db24bd087758527829c773e` |
| source_uri | `models:/m-9843c06fd4844278a4e39e86c6652eb2` |
| dataset_fingerprint | `3ecba3895569060b1a25418d1cac3171b782fd2554f0275d759990c7b013c354` |
| model_type | `logistic_regression` |

Note that `source_uri` is a **Logged Model** URI (`models:/m-...`), not the legacy `runs:/{run_id}/model` path — this is expected under MLflow 3.x, where models are logged as first-class entities rather than as files under a run's artifact directory (see Design Separation and the note under Model Loading below).

## Model Loading

The model was successfully loaded from the registry by alias:

`models:/Sprint08FraudDetectionModel@candidate`

The loaded object is the complete sklearn `Pipeline`.

**This load only succeeds because of a fix made during this sprint day.** MLflow 3.x logs models (when called with `name=` rather than `artifact_path=`) as separate "Logged Model" entities — they are not written under the run's own artifact directory, and the previously-used `runs:/{run_id}/model` convention for registering them no longer resolves in this MLflow version. `MLflowTracker.log_model_run` now captures the real `model_uri` returned by `mlflow.sklearn.log_model(...)` and tags the run with it; `ModelRegistryService.register_run_model` reads that tag back and uses it as the registration source, falling back to the deprecated `runs:/` scheme only for runs logged before this fix existed. Any Day 4 data logged prior to this fix had to be regenerated (`rm -rf artifacts/mlflow` then re-running Day 4) before Day 5 could register and load successfully — registering against stale pre-fix runs reproduces the original `MlflowException: No such artifact: 'MLmodel'` failure, since those runs were never tagged with a resolvable model URI.

## Model Versioning

Every registration creates an immutable version under the same registered model name.

Historical versions can therefore remain available while the candidate alias moves between versions.

## Alias Strategy

MLflow model aliases are used rather than deprecated stage-based lifecycle APIs.

Current lifecycle marker:

`candidate`

Future lifecycle markers may include:

- `champion`
- `challenger`
- `rollback`

but Day 5 does not assign production approval.

## Design Separation

**Day 4:** tracks experiments.

**Day 5:** registers lifecycle candidates.

**Day 6:** validates candidates.

Registration is not equivalent to approval.

## Limitations

Day 5 does not implement:

- data-quality validation
- minimum model metric gates
- candidate-vs-baseline validation
- production deployment
- cloud registry
- CI/CD
- automatic rollback

## Validation

Focused:
```bash
uv run pytest ml/tests/test_day05_registry.py -v
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
uv run python -m ml.scripts.run_day05
```

## Result

Day 5 is complete: a model was registered (`Sprint08FraudDetectionModel`, version `1`); the version exists and is listed correctly (`Registered versions` shows exactly one entry, `run=b7e13a823db24bd087758527829c773e`); source-run lineage is preserved (source run ID, model type, and dataset fingerprint all traced back correctly); the `candidate` alias exists and resolves; `validation_status=pending` is stored as a tag; versions can be listed; and the model was successfully loaded by alias, returning a live `Pipeline` object.

Two real bugs were found and fixed to get here, both worth carrying forward into Day 6 and beyond:

1. **`ModelVersion.version` was returning a raw `int` at runtime** despite MLflow's own class declaring it as `str` — `ModelRegistryService._to_info` now explicitly coerces with `str(model_version.version)` rather than trusting the declared type.
2. **MLflow 3.x's model-URI behavior change** (models as first-class Logged Model entities, not run artifacts) broke the deprecated `runs:/{run_id}/model` convention this codebase originally relied on for registration and loading. The fix captures the real `model_uri` from `log_model`'s return value at logging time, tags the run with it, and has the registry prefer that tag over the legacy scheme — with graceful fallback for any pre-existing runs logged before the fix.