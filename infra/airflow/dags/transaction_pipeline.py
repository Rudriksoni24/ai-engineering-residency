"""Sprint 9 Day 5 transaction processing DAG."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow.sdk import dag, task

from streaming.orchestration.pipeline import (
    generate_report,
    generate_transactions,
    process_transactions,
    validate_transactions,
)

ARTIFACT_ROOT = Path(
    "/opt/airflow/project/artifacts/sprint09/day05/airflow"
)


@dag(
    dag_id="sprint09_transaction_pipeline",
    schedule=None,
    start_date=datetime(
        2026,
        9,
        1,
    ),
    catchup=False,
    tags=[
        "sprint09",
        "transactions",
        "spark",
    ],
)
def transaction_pipeline():
    @task
    def generate() -> str:
        path = (
            ARTIFACT_ROOT
            / "transactions.json"
        )

        generate_transactions(
            path,
            count=20,
            seed=42,
        )

        return str(path)

    @task
    def validate(
        input_path: str,
    ) -> str:
        path = (
            ARTIFACT_ROOT
            / "validated.json"
        )

        validate_transactions(
            Path(input_path),
            path,
        )

        return str(path)

    @task
    def process(
        input_path: str,
    ) -> str:
        path = (
            ARTIFACT_ROOT
            / "account_summary.json"
        )

        process_transactions(
            Path(input_path),
            path,
        )

        return str(path)

    @task
    def report(
        input_path: str,
    ) -> str:
        path = (
            ARTIFACT_ROOT
            / "workflow_report.json"
        )

        generate_report(
            Path(input_path),
            path,
        )

        return str(path)

    raw = generate()
    validated = validate(raw)
    processed = process(validated)

    report(processed)


transaction_pipeline()