# Sprint 9 — Day 6 Report

## Title

Delta Lake and Data Contracts

## Artifact

Lakehouse Pipeline

## Architecture

```text
Transaction
    |
    v
Pydantic Contract
    |
    v
Spark DataFrame
    |
    v
Bronze Delta
    |
    v
Silver Delta
    |
    v
Gold Delta