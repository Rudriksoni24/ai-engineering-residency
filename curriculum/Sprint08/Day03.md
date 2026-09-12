# Sprint 8 — Day 3: Fraud Detection Modeling

Artifact: Fraud Detection Model

## Goal

Build and compare multiple classical models for an imbalanced fraud-detection
problem using identical data, preprocessing, and evaluation methodology.

## 1. Class Imbalance

Fraud datasets typically contain far fewer positive fraud cases than
legitimate transactions.

Example:

- legitimate: 97%
- fraud: 3%

A classifier that predicts every transaction as legitimate may achieve high
accuracy while detecting no fraud.

Therefore accuracy alone is not sufficient.

## 2. False Positives

False positive:

actual legitimate transaction
predicted fraud

Consequences may include:

- blocked customer transaction
- support cost
- poor customer experience
- unnecessary manual review

## 3. False Negatives

False negative:

actual fraud
predicted legitimate

Consequences may include:

- financial loss
- fraud exposure
- reimbursement cost
- compliance risk

The relative cost of false positives and false negatives determines the
appropriate threshold and model-selection policy.

## 4. Precision

Precision asks:

Of transactions predicted as fraud, how many were actually fraud?

precision = TP / (TP + FP)

High precision reduces false alarms.

## 5. Recall

Recall asks:

Of all real fraud cases, how many did we detect?

recall = TP / (TP + FN)

Fraud systems often care strongly about recall because missed fraud can be
expensive.

Higher recall may, however, increase false positives.

## 6. F1

F1 is the harmonic mean of precision and recall.

F1 = 2 * precision * recall / (precision + recall)

It is useful when both precision and recall matter, but it still does not
encode a real business cost function.

## 7. Probability Scores

Many classifiers produce:

predict_proba(X)

For binary classification:

P(fraud = 1)

Examples:

0.02
0.18
0.47
0.81
0.96

The final class prediction depends on a threshold.

Default:

probability >= 0.5 -> fraud

The default threshold is a software convention, not a business truth.

## 8. Threshold Selection

Lower threshold:

- usually increases recall
- usually increases false positives
- usually decreases precision

Higher threshold:

- usually increases precision
- usually decreases recall
- usually increases false negatives

Threshold selection must match operational objectives.

## 9. ROC Curve

ROC examines:

True Positive Rate
vs
False Positive Rate

over many thresholds.

ROC-AUC summarizes ranking performance.

A value near:

0.5 -> random ranking
1.0 -> perfect ranking

However ROC-AUC can appear optimistic on highly imbalanced datasets because
true negatives dominate the negative class.

## 10. Precision-Recall Curve

Precision-Recall analysis focuses directly on the positive class.

For rare fraud problems, PR-AUC / Average Precision is often more
informative than ROC-AUC.

Average Precision summarizes performance across recall levels.

## 11. Class Weighting

A model can assign additional importance to minority fraud examples.

Example:

class_weight="balanced"

For Logistic Regression or Random Forest, this changes training so minority
errors carry more weight.

Class weighting does not modify the dataset itself.

It modifies the learning objective.

## 12. Models Compared

Day 3 compares:

- Logistic Regression
- Random Forest
- HistGradientBoosting

The purpose is not benchmark optimization.

The purpose is understanding model behavior under identical evaluation.

## 13. Fair Comparison

Every model must use:

- the same source dataset
- the same train/test split
- the same engineered feature transformation
- the same evaluation functions
- the same seed where supported

Otherwise model comparison becomes confounded.

## 14. Candidate Selection

The selected candidate should not automatically be:

highest accuracy

A fraud candidate should consider:

- recall
- precision
- F1
- ROC-AUC
- average precision
- operational threshold

The selection policy must be explicit.

## 15. Day 3 Boundary

Implemented today:

- class imbalance analysis
- multiple classical models
- class weighting where supported
- probability scores
- precision/recall tradeoff
- threshold selection
- ROC-AUC
- average precision
- confusion matrix comparison
- deterministic model comparison
- selected candidate model

Not implemented today:

- MLflow tracking
- model registry
- promotion aliases
- data validation framework
- production deployment