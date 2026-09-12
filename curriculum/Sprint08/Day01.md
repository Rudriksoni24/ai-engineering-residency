# Sprint 8 — Day 1: Classical ML Pipeline

Artifact: ML Pipeline

## Goal

Build a complete classical supervised machine-learning pipeline from raw
structured data through model training and evaluation.

## 1. Supervised Learning

Supervised learning learns a mapping:

X -> y

where:

- X represents input features.
- y represents the target or label.

For binary fraud classification:

y = 0 -> legitimate transaction
y = 1 -> fraudulent transaction

The model learns patterns from historical labeled examples.

## 2. Features

Features are the variables available to the model.

Examples:

- transaction amount
- transaction type
- account age
- transaction hour
- merchant category
- country risk indicator
- previous transaction frequency
- account balance

Features should represent information that would realistically be available
when prediction occurs.

## 3. Target

The target is the value being predicted.

For this Sprint:

fraud_label

Possible values:

0 = legitimate
1 = fraud

The target must never accidentally be included in the feature matrix.

That would be target leakage.

## 4. Classification

Classification predicts discrete categories.

Binary classification has two classes.

Our problem:

legitimate vs fraud

Other ML problem types include regression, clustering, ranking, and anomaly
detection, but Day 1 focuses only on supervised binary classification.

## 5. Training Set

The training set is used to learn:

- preprocessing parameters
- category encodings
- scaling statistics
- model coefficients

The model is allowed to learn from this data.

## 6. Test Set

The test set estimates behavior on unseen data.

The model must not learn from test data.

The test set is used only after training is complete.

## 7. Data Leakage

Data leakage occurs when information unavailable during real prediction
accidentally influences training.

Examples:

- including the fraud label as a feature
- calculating preprocessing statistics using all data before splitting
- using future transaction information
- selecting model parameters based repeatedly on test-set results

Leakage creates unrealistically optimistic metrics.

## 8. Preprocessing

Machine-learning estimators usually require numerical matrices.

Structured business data often contains:

- numeric fields
- categorical fields
- missing values

Our baseline preprocessing uses:

Numeric:
- median imputation
- standard scaling

Categorical:
- most-frequent imputation
- one-hot encoding

No derived fraud features are introduced on Day 1.

Those belong to Sprint 8 Day 2.

## 9. Fit vs Transform

fit():

Learns parameters from data.

Examples:

- median
- mean
- standard deviation
- category vocabulary
- model coefficients

transform():

Uses already learned preprocessing parameters to transform data.

fit_transform():

Learns parameters and immediately transforms the same data.

Correct workflow:

training data -> fit_transform
test data     -> transform

Scikit-learn Pipeline protects this workflow when the train/test split occurs
before pipeline.fit().

## 10. Estimator

An estimator is an algorithm that learns from data.

Day 1 uses:

LogisticRegression

It is a good baseline because it is:

- simple
- fast
- interpretable
- probabilistic
- suitable for binary classification

More sophisticated fraud models belong to Day 3.

## 11. Prediction

After training:

model.predict(X_test)

produces predicted classes.

For example:

0
1
0
0

Prediction is separate from training.

## 12. Evaluation

Accuracy alone is insufficient for many fraud problems.

Suppose:

99% legitimate
1% fraud

A model predicting every transaction as legitimate gets:

99% accuracy

but:

0% fraud recall

Therefore Day 1 records:

- accuracy
- precision
- recall
- F1
- confusion matrix

Later Sprint days add ROC-AUC, PR-AUC, threshold selection, model comparison,
and fraud-specific decision tradeoffs.

## 13. Confusion Matrix

For binary classification:

             Predicted 0    Predicted 1

Actual 0         TN              FP
Actual 1         FN              TP

TN = true negative
FP = false positive
FN = false negative
TP = true positive

For fraud detection:

False positive:
legitimate transaction incorrectly flagged.

False negative:
fraud transaction incorrectly accepted.

These errors have different business costs.

## 14. Reproducibility

Machine-learning experiments are meaningful only when their inputs and
randomness are controlled.

Day 1 controls:

- dataset generator seed
- train/test split seed
- estimator random_state
- dataset size
- test fraction

The same configuration should produce the same result.

## 15. Day 1 Architecture

Raw Synthetic Transactions
        |
        v
Basic Dataset Validation
        |
        v
Features / Target Separation
        |
        v
Stratified Train/Test Split
        |
        v
ColumnTransformer
        |
        +---- Numeric preprocessing
        |
        +---- Categorical preprocessing
        |
        v
LogisticRegression
        |
        v
Predictions
        |
        v
Classification Metrics

## Day 1 Boundary

Implemented today:

- deterministic dataset
- validation
- train/test split
- baseline preprocessing
- Logistic Regression
- predictions
- evaluation
- deterministic tests

Not implemented today:

- derived feature engineering
- model comparison
- fraud threshold optimization
- class weighting experiments
- MLflow
- registry
- lifecycle promotion
- production deployment

## Architecture 
ml.data.synthetic
        │
        │ generate raw observations
        ▼
DataFrame
        │
        ▼
ml.training.pipeline
        │
        ├── validate raw schema
        ├── separate X / y
        ├── train/test split
        │
        ▼
ml.models.baseline
        │
        ├── numerical preprocessing
        ├── categorical preprocessing
        └── LogisticRegression
        │
        ▼
ml.training.pipeline
        │
        ├── fit
        ├── predict
        └── evaluate
        │
        ▼
TrainingResult