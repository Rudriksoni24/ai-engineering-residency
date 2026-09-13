# Sprint 8 — Day 4: Experiment Tracking with MLflow

Artifact: MLflow Tracking System

## Goal

Make classical machine-learning experiments observable, comparable, and reproducible using local MLflow tracking.

## Experiment

An MLflow experiment is a logical container for related runs.

For Day 4:

Sprint08-Fraud-Experiments

contains several model-training runs.

## Run

A run represents one execution of an experiment configuration.

Each run records:

* run ID
* parameters
* metrics
* tags
* artifacts
* model artifact
* reproducibility metadata

## Run ID

Every MLflow run receives a unique identifier.

A run ID allows us to connect:

configuration
→ metrics
→ artifacts
→ model

without relying on terminal output.

## Parameters

Parameters describe configuration choices.

Examples:

model_type
random_seed
test_size
class_weight
n_estimators
max_depth
learning_rate

Parameters usually describe things chosen before training.

## Metrics

Metrics describe measured outcomes.

Examples:

accuracy
precision
recall
F1
ROC-AUC
Average Precision

Metrics are numerical observations produced by an experiment.

## Tags

Tags provide searchable metadata that is neither a model parameter nor a metric.

Examples:

sprint = 8
day = 4
artifact = MLflow Tracking System
dataset = synthetic-banking-fraud

## Artifacts

Artifacts are files associated with a run.

Day 4 stores artifacts such as:

confusion_matrix.json
reproducibility.json
model

## Tracking URI

The tracking URI tells MLflow where experiment metadata is stored.

Day 4 uses a local SQLite backend.

No cloud account, Databricks workspace, or remote object storage is required.

## Dataset Fingerprint

A training run should identify the dataset it used.

Day 4 computes a SHA-256 fingerprint from normalized dataset contents.

This creates an association:

training run
↔
dataset version

Git alone does not provide dataset versioning.

## Reproducibility Metadata

A reproducible run should expose:

dataset fingerprint
random seed
test size
model type
model configuration
preprocessing configuration
metrics

Hidden configuration makes experiments difficult to reproduce.

## Parent and Child Runs

Day 4 compares several models in one logical execution.

A parent run represents the comparison session.

Child runs represent individual models.

Example:

Day 4 Comparison
├── Logistic Regression
├── Random Forest
└── HistGradientBoosting

This preserves both group-level and individual-run identity.

## Manual Tracking

MLflow supports manual tracking.

Conceptually:

start run
↓
log parameters
↓
train model
↓
calculate metrics
↓
log metrics
↓
log artifacts
↓
log model
↓
end run

Day 4 deliberately builds a reusable tracking service rather than scattering MLflow calls through model-training code.

## Multiple Runs

The same dataset and split are used for:

Logistic Regression
Random Forest
HistGradientBoosting

Each receives its own child run.

This makes experimental comparison persistent rather than relying on transient console output.

## Experiment Comparison

Runs can be ranked using metrics such as:

Average Precision
ROC-AUC
recall
F1

For the current fraud problem, Average Precision remains the primary comparison metric.

Accuracy is not the primary selection signal because the target is imbalanced.

## Local Storage

Day 4 uses local storage:

artifacts/mlflow/mlflow.db

and:

artifacts/mlflow/artifacts/

These files are generated runtime state and should not be committed.

## Model Artifact

The complete sklearn Pipeline is logged as the model artifact.

This preserves:

feature engineering
preprocessing
classifier

as one model object.

The artifact is associated with the MLflow run that generated it.

Registration and promotion are intentionally deferred to Day 5.

## Day 4 Boundary

Implemented today:

MLflow dependency
local tracking backend
experiments
runs
run IDs
parameters
metrics
tags
artifacts
model logging
dataset fingerprint
reproducibility metadata
parent/child runs
multiple tracked runs
run comparison

Not implemented today:

registered models
model versions
aliases
production promotion
validation gates
deployment
cloud MLflow
