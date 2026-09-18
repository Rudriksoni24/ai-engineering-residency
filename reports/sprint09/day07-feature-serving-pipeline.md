# Sprint 9 — Day 7 Report

## Title

Feast Feature Store

## Artifact

Feature Serving Pipeline

## Architecture

Transactions
→ Feature Engineering
→ Offline Feature Data
→ Feast
→ Historical Retrieval / Online Materialization
→ Feature Serving

## Entity

account

Join key:

account_id

## Features

- transaction_count_1h
- avg_transaction_amount_1h
- max_transaction_amount_1h
- recent_country_count
- recent_high_risk_merchant_count

## Offline Features

Historical features are retrieved using entity identifiers and event
timestamps.

The historical retrieval path is intended for training and batch feature
retrieval.

## Point-in-Time Correctness

Feature engineering excludes transactions occurring after the requested
feature timestamp.

This prevents future information from leaking into historical feature values.

## Online Features

Features are materialized into a local SQLite online store.

Online retrieval returns current serving values for an account.

## Training-Serving Consistency

The same Feast feature definitions identify features for historical and
online retrieval.

## Feature Freshness

Online values are only as fresh as the ingestion/materialization strategy.

A feature store does not automatically guarantee real-time freshness.

## Local Architecture

- local Feast provider
- Parquet feature source
- local registry
- SQLite online store
- synthetic banking data

## Production Differences

Production systems may use:

- distributed feature computation
- cloud warehouses/lakes
- streaming feature pipelines
- distributed online stores
- feature monitoring
- lineage
- automated materialization
- freshness SLAs

## Sprint 9 Exit Criteria

- [x] Understand offline and online features.
- [x] Use a feature store.