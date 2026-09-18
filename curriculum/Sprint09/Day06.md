# Sprint 9 — Day 6: Delta Lake and Data Contracts

## Artifact

Lakehouse Pipeline

## Objective

Build an explicit transaction data contract and persist validated analytical
data using Delta Lake.

## Architecture

```text
Raw Transaction
      |
      v
Pydantic Contract
      |
      v
Validated Transaction
      |
      v
Bronze Delta
      |
      v
Silver Delta
      |
      v
Gold Delta