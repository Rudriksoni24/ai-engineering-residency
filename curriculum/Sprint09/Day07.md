# Sprint 9 — Day 7: Feast Feature Store

## Artifact

Feature Serving Pipeline

## Objective

Build a local feature-serving pipeline using Feast and understand how feature
stores support machine-learning training and inference.

By the end of this day, we should understand:

- entities
- features
- feature views
- feature sources
- offline feature storage
- online feature storage
- historical feature retrieval
- point-in-time correctness
- materialization
- online feature retrieval
- feature freshness
- training-serving skew


# 1. Why Feature Stores Exist

Machine-learning systems consume features rather than raw application events.

For example, a transaction system may produce:

```text
transaction_id
account_id
amount
merchant_category
timestamp
country