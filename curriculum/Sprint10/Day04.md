# Sprint 10 — Day 4: Airflow and Spark on Kubernetes

**Artifact:** Kubernetes-Orchestrated Batch Pipeline

## Objective

Deploy the existing Sprint 9 transaction-processing Airflow DAG
inside the Sprint 10 kind cluster.

Execute the existing transaction pipeline, including its real
PySpark batch aggregation.

Persist pipeline output on a Kubernetes PersistentVolumeClaim.

Verify that the completed output survives Airflow Pod replacement.

## Existing Components Reused

- `infra/airflow/dags/transaction_pipeline.py`
- `streaming/orchestration/pipeline.py`
- `streaming/events.py`
- `streaming/spark/batch.py`
- `streaming/spark/schemas.py`

Do not create a duplicate transaction generator, Spark aggregation,
or demonstration API.

## Architecture

```text
kind cluster: ai-residency
  |
  +-- namespace: ai-platform
        |
        +-- Existing local-llm-api Deployment
        |
        +-- Existing PostgreSQL and MinIO StatefulSets
        |     (may be scaled to zero to conserve memory)
        |
        +-- airflow-spark Deployment
              |
              +-- Airflow standalone
              |     |
              |     +-- DAG: sprint09_transaction_pipeline
              |           |
              |           +-- generate
              |           +-- validate
              |           +-- process
              |           |     |
              |           |     +-- Spark local[2]
              |           +-- report
              |
              +-- PVC: airflow-spark-artifacts
                    |
                    +-- persisted workflow artifacts
```

## Airflow Responsibilities

Airflow defines and executes task dependencies.

The DAG has four tasks:

1. Generate deterministic transaction input.
2. Validate transaction records.
3. Process transactions using the existing PySpark implementation.
4. Produce a workflow-completion report.

A successful DAG run requires every task to succeed.

## Spark Responsibilities

The `process` task starts Spark using `local[2]`.

Spark performs a grouped aggregation by account.

Spark is running inside the Airflow container for this local
learning deployment.

This is not a distributed Spark-on-Kubernetes deployment.

## Persistence

The workflow's existing artifact directory is backed by a
Kubernetes PVC.

Pod replacement must not delete the completed output.

Airflow's standalone SQLite metadata database and local task logs
are not treated as production-grade durable services in this lab.

The persistent output, rather than Airflow metadata, is the
recovery target for today's demonstration.

## Runtime and Resources

The container requires:

- Airflow 3.1.0
- PySpark 4.1.1
- Java 17 or a compatible installed Java runtime
- Existing repository streaming code
- Existing Airflow transaction DAG

Airflow standalone runs several processes inside one Pod.

Inspect cluster memory before starting this deployment.

Scale down unused Day 3 StatefulSets if necessary, preserving
their PVCs.

## Tests

1. Container image builds for linux/arm64.
2. Image runs Airflow and provides Java and PySpark.
3. Kubernetes PVC becomes Bound.
4. Airflow Deployment reaches 1/1 Ready.
5. Airflow UI is reachable through port-forward.
6. The existing transaction DAG appears.
7. DAG tasks run in the required dependency order.
8. The Spark processing task succeeds.
9. Workflow report records 20 transactions.
10. Output survives Airflow Pod replacement.
11. Existing Day 2 application is preserved.
12. Existing Day 3 PVCs remain intact.
13. Existing repository regression tests pass.

## Limitations

This setup is intended for local Kubernetes learning.

Airflow standalone is not a production multi-component
Airflow architecture.

Spark executes in local mode inside the Airflow Pod.

The workflow is small and uses synthetic data.

The existing DAG writes artifacts to its Sprint 9 path, which
is mounted to a Day 4 Kubernetes PVC for this deployment.

The Day 3 PostgreSQL instance is not silently repurposed as
Airflow's metadata database.

No existing PostgreSQL or MinIO data is migrated or deleted.

## Day 4 Exit Gate

- [ ] Day 3 data preserved.
- [ ] Airflow/Spark image built successfully.
- [ ] Java available inside image.
- [ ] PySpark available inside image.
- [ ] Airflow artifacts PVC Bound.
- [ ] Airflow Deployment Ready.
- [ ] Airflow UI accessible.
- [ ] Existing DAG visible.
- [ ] Four-task DAG run successful.
- [ ] Spark processing task confirmed successful.
- [ ] Workflow report contains 20 transactions.
- [ ] Output survives Pod replacement.
- [ ] Existing FastAPI application preserved.
- [ ] Existing Day 3 PVCs preserved.
- [ ] Full repository regression passes.
- [ ] Engineering report updated with actual results.
- [ ] Day 4 committed and merged.

**Artifact:** Kubernetes-Orchestrated Batch Pipeline