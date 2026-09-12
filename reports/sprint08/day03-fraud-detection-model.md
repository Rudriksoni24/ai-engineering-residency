# Sprint 8 — Day 3 Report

## Title

Sprint 8 — Day 3: Fraud Detection Modeling

## Artifact

Fraud Detection Model

## Objective

Evaluate multiple classical classifiers for an imbalanced fraud-detection problem using identical data, preprocessing, and evaluation methodology.

The goal was not to maximize accuracy. The experiment focused on fraud-sensitive metrics including precision, recall, F1, ROC-AUC, Average Precision, confusion matrices, and threshold behavior.

---

## Dataset

The Day 3 experiment used a deterministic synthetic banking transaction dataset.

Configuration:

* Total rows: 5,000
* Training rows: 4,000
* Test rows: 1,000
* Fraud rate: 7.58%
* Random seed: 42
* Test size: 20%

The dataset is imbalanced, making accuracy insufficient as the primary model-selection metric.

---

## Models Compared

Three classical models were evaluated:

1. Logistic Regression
2. Random Forest
3. HistGradientBoosting

All models used:

* the same source dataset
* the same deterministic train/test split
* the same engineered feature transformation
* the same preprocessing approach
* identical evaluation methodology

Class weighting was explicitly used where supported by the Day 3 implementation.

---

## Model Results

### Logistic Regression

Selected threshold:

```text
0.4272
```

Metrics:

```text
Accuracy:           0.5780
Precision:          0.1303
Recall:             0.8026
F1:                 0.2243
ROC-AUC:            0.7422
Average Precision:  0.2254
```

Confusion matrix:

```text
[[TN, FP],
 [FN, TP]]

[[517, 407],
 [ 15,  61]]
```

Interpretation:

* 61 fraud transactions were correctly detected.
* 15 fraud transactions were missed.
* 407 legitimate transactions were incorrectly flagged as fraud.
* Fraud recall reached 80.26%.
* Precision remained low at 13.03%.

The lower threshold increased fraud detection substantially, but it also created a large number of false positives.

---

### Random Forest

Threshold:

```text
0.5000
```

Metrics:

```text
Accuracy:           0.7910
Precision:          0.1444
Recall:             0.3553
F1:                 0.2053
ROC-AUC:            0.6944
Average Precision:  0.1413
```

Confusion matrix:

```text
[[764, 160],
 [ 49,  27]]
```

Interpretation:

Random Forest produced substantially higher accuracy than Logistic Regression but detected only 35.53% of fraudulent transactions.

It generated fewer false positives than the selected Logistic Regression configuration, but it missed 49 of the 76 fraud cases in the test set.

This demonstrates why accuracy alone would be misleading for this problem.

---

### HistGradientBoosting

Threshold:

```text
0.5000
```

Metrics:

```text
Accuracy:           0.9180
Precision:          0.2857
Recall:             0.0526
F1:                 0.0889
ROC-AUC:            0.6538
Average Precision:  0.1551
```

Confusion matrix:

```text
[[914, 10],
 [ 72,  4]]
```

Interpretation:

HistGradientBoosting achieved the highest accuracy and precision of the three models at the evaluated threshold.

However, fraud recall was only 5.26%.

The model detected only 4 of the 76 fraud transactions and missed 72.

Therefore, despite its 91.8% accuracy, it is unsuitable as the Day 3 candidate under the fraud-focused selection policy.

---

## Model Comparison

| Model                |   Accuracy |  Precision |     Recall |         F1 |    ROC-AUC | Average Precision |
| -------------------- | ---------: | ---------: | ---------: | ---------: | ---------: | ----------------: |
| Logistic Regression  |     0.5780 |     0.1303 | **0.8026** | **0.2243** | **0.7422** |        **0.2254** |
| Random Forest        |     0.7910 |     0.1444 |     0.3553 |     0.2053 |     0.6944 |            0.1413 |
| HistGradientBoosting | **0.9180** | **0.2857** |     0.0526 |     0.0889 |     0.6538 |            0.1551 |

The experiment demonstrates that the model with the highest accuracy was not the strongest fraud detector.

HistGradientBoosting achieved:

```text
91.80% accuracy
```

but only:

```text
5.26% recall
```

Logistic Regression achieved much lower accuracy but captured:

```text
80.26% of fraud cases
```

This confirms why accuracy cannot be the primary metric for an imbalanced fraud problem.

---

## Selected Candidate

Selected model:

```text
Logistic Regression
```

Selected threshold:

```text
0.4272
```

Candidate-selection policy:

1. Highest Average Precision
2. Highest recall
3. Highest F1

Observed ranking evidence:

```text
Logistic Regression
Average Precision = 0.2254
ROC-AUC           = 0.7422
Recall            = 0.8026
F1                = 0.2243
```

Logistic Regression had the highest Average Precision and ROC-AUC of the evaluated models.

It was therefore selected as the Day 3 candidate model.

---

## Threshold Analysis

The selected Logistic Regression threshold was reduced from the conventional default of:

```text
0.5000
```

to:

```text
0.4272
```

to satisfy the configured minimum recall requirement.

Resulting recall:

```text
0.8026
```

This demonstrates that model training and decision policy are separate concerns.

The classifier generates fraud probabilities or scores.

The threshold converts those scores into business decisions.

Changing the threshold does not retrain the model.

---

## Precision / Recall Tradeoff

The selected model exposes an important operational tradeoff.

Confusion matrix:

```text
TN = 517
FP = 407
FN = 15
TP = 61
```

The model successfully detects most fraud:

```text
Recall = 80.26%
```

but generates many false alarms:

```text
407 false positives
```

for:

```text
61 true positives
```

This explains the relatively low precision:

```text
Precision = 13.03%
```

Therefore, the selected candidate should not yet be interpreted as a production-ready fraud decision system.

A production system would need to consider:

* cost of missed fraud
* cost of manual review
* customer friction
* false-positive capacity
* transaction value
* risk tolerance
* probability calibration
* threshold policy

---

## ROC-AUC vs Average Precision

Logistic Regression achieved:

```text
ROC-AUC = 0.7422
Average Precision = 0.2254
```

The difference is meaningful.

ROC-AUC indicates that the model has useful ranking ability between fraudulent and legitimate transactions.

Average Precision is substantially lower because the positive fraud class is rare and precision deteriorates as recall increases.

For this imbalanced fraud problem, Average Precision provides an important complement to ROC-AUC.

---

## Class Imbalance Finding

The dataset fraud rate was:

```text
7.58%
```

The experiment clearly demonstrates how imbalance affects metric interpretation.

HistGradientBoosting:

```text
Accuracy = 91.80%
Recall   = 5.26%
```

A system evaluated mainly by accuracy could incorrectly favor this model.

Fraud-specific evaluation instead reveals that it misses nearly all fraudulent transactions at the evaluated threshold.

---

## Candidate Selection Result

Final Day 3 candidate:

```text
Model:
Logistic Regression

Threshold:
0.4272

Accuracy:
0.5780

Precision:
0.1303

Recall:
0.8026

F1:
0.2243

ROC-AUC:
0.7422

Average Precision:
0.2254
```

Candidate selection is supported by the actual experiment results rather
