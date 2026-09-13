# Sprint 8 — Day 5: Model Registry

Artifact: Model Lifecycle Pipeline

## Goal

Manage trained ML models as versioned lifecycle entities rather than loose
artifact files.

## 1. Model Artifact

A model artifact is the serialized model produced by a training run.

For this Sprint, the artifact contains the full sklearn Pipeline:

raw input
    ↓
feature transformer
    ↓
preprocessing
    ↓
classifier

A model artifact is associated with an MLflow run.

## 2. Registered Model

A registered model is a named logical model in the MLflow Model Registry.

Example:

FraudDetectionModel

It acts as the container for multiple model versions.

## 3. Model Version

Each registration produces a version.

Example:

FraudDetectionModel

Version 1
Version 2
Version 3

Versions are immutable lifecycle references to specific model artifacts.

## 4. Training Run vs Registered Model

A training run records:

- parameters
- metrics
- tags
- artifacts
- dataset fingerprint
- model artifact

A registered model provides:

- stable logical name
- versions
- aliases
- lifecycle metadata

One training run may become a registered model version.

Not every experiment run should necessarily be registered.

## 5. Source Run Lineage

A model version should preserve the run that produced it.

The relationship is:

registered model version
        ↓
source run ID
        ↓
parameters
metrics
dataset fingerprint
artifacts

This provides lineage.

## 6. Model URI

Examples:

Run artifact:

runs:/<run_id>/model

Specific registered version:

models:/FraudDetectionModel/3

Alias:

models:/FraudDetectionModel@candidate

Registry URIs provide stable references to model artifacts.

## 7. Candidate Model

A candidate model is a model version selected for further evaluation.

Candidate does not mean production-approved.

Day 5 uses the alias:

candidate

to identify the version selected from tracked experiments.

## 8. Aliases

Aliases are mutable names pointing to specific immutable model versions.

Example:

candidate -> version 3

Later:

candidate -> version 4

The version remains immutable, while the alias can move.

Aliases are preferred over deprecated stage-based APIs.

## 9. Lifecycle Tags

Model version tags can express metadata such as:

lifecycle_status=candidate
validation_status=pending
source=sprint08-day05

Tags describe state without changing the model artifact itself.

## 10. Loading by Registry Identifier

A version can be loaded using:

models:/FraudDetectionModel/1

An alias can be loaded using:

models:/FraudDetectionModel@candidate

Consumers therefore do not need to know the original run ID.

## 11. Versioning

Each newly registered candidate becomes another version under the same logical
model name.

Example:

FraudDetectionModel
├── Version 1
├── Version 2
└── Version 3

The registry preserves historical artifacts rather than overwriting a single
best_model.pkl file.

## 12. Promotion

Day 5 demonstrates lifecycle promotion using aliases and tags.

Example:

candidate
    ↓
Version 2

Future validation can determine whether the candidate deserves an approved
or champion-style lifecycle marker.

Day 5 does not perform Day 6 validation.

## 13. Local Registry

The Model Registry uses the same local MLflow SQLite backend created on Day 4.

No cloud registry is required.

## 14. Day 5 Boundary

Implemented today:

- registered model
- model versions
- model URI
- source-run lineage
- aliases
- lifecycle tags
- retrieve versions
- load model by registry identifier
- versioned artifacts
- candidate promotion

Not implemented today:

- formal data validation
- model-quality validation gates
- baseline-vs-candidate acceptance
- production deployment
- Kubernetes
- CI/CD