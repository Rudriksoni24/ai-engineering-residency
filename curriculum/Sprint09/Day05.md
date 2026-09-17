# Sprint 9 — Day 5: Airflow Orchestration

## Artifact

Data Workflow DAG

## Objective

Understand workflow orchestration using Apache Airflow while keeping business
processing outside the orchestrator.

## Architecture

```text
Airflow Scheduler
       |
       v
Generate Data
       |
       v
Validate Data
       |
       v
Spark Batch Processing
       |
       v
Generate Report