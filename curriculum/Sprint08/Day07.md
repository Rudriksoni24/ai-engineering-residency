# Sprint 8 — Day 7: Sprint Integration

Artifact: Reproducible ML Platform

## Goal

Integrate Sprint 8 Days 1–6 into one reproducible local machine-learning
platform.

Day 7 introduces orchestration, not a new machine-learning methodology.

## Integrated Workflow

Raw Data
    ↓
Data Validation
    ↓
Dataset Fingerprint
    ↓
Train/Test Split
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

## Reproducibility

A reproducible run controls:

- synthetic dataset seed
- dataset size
- train/test split seed
- test fraction
- model configuration
- feature transformations
- preprocessing
- candidate-selection policy
- validation policy

A repeated execution with identical inputs should reproduce:

- dataset fingerprint
- model ranking
- selected model
- evaluation metrics

Run IDs and registry version numbers will differ because those represent new
execution/lifecycle records.

## Data Identity

The deterministic dataset fingerprint associates:

training workflow
↔
dataset contents

The same deterministic generated dataset should produce the same fingerprint.

## Experiment Tracking

Each candidate model is logged to MLflow with:

- parameters
- metrics
- tags
- confusion matrix
- reproducibility metadata
- model artifact

Model URIs returned by MLflow are preserved directly.

The orchestration layer must not reconstruct deprecated model artifact URIs.

## Candidate Selection

Candidates are compared primarily using:

Average Precision

with deterministic tie-break rules defined by the existing training/tracking
components.

Candidate selection is separate from candidate validation.

## Model Validation

The selected model must pass:

- prediction checks
- metric checks
- baseline comparison

before becoming promotion eligible.

## Registry Lifecycle

A validated model is registered under:

Sprint08FraudDetectionModel

A new immutable model version is created.

Lifecycle aliases provide mutable references to immutable versions.

Day 7 uses:

candidate

and when validation passes:

validated

The platform does not claim production deployment.

## Important Distinction

Reproducible outputs:

- dataset fingerprint
- metrics
- selected model
- parameters

Expected to change across executions:

- MLflow run ID
- registered model version
- artifact record identifiers

Reproducibility does not mean database-generated IDs remain identical.

## Platform Output

The final workflow reports:

- dataset fingerprint
- seed
- selected model
- parameters
- metrics
- MLflow run ID
- MLflow model URI
- registered model name
- registered version
- registry URI
- validation status
- promotion eligibility

## Day 7 Boundary

Implemented:

- complete Sprint integration
- deterministic data generation
- data validation
- feature engineering
- multiple-model training
- evaluation
- MLflow tracking
- run comparison
- candidate selection
- model validation
- registration
- model versioning
- lifecycle alias
- reproducibility verification

Not implemented:

- Kubernetes
- CI/CD
- online serving
- streaming pipelines
- production monitoring
- deployment