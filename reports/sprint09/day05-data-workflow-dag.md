# Sprint 9 — Day 5 Report

## Title

Airflow Orchestration

## Artifact

Data Workflow DAG

## Architecture

```text
Generate Transactions
        |
        v
Validate Transactions
        |
        v
Spark Batch Processing
        |
        v
Generate Report