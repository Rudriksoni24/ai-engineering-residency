"""Application operations orchestrated by the Day 5 workflow."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from streaming.events import TransactionGenerator


def generate_transactions(
    output_path: Path,
    *,
    count: int = 20,
    seed: int = 42,
) -> Path:
    """Generate deterministic synthetic transaction data."""
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    generator = TransactionGenerator(
        seed=seed,
    )

    events = generator.generate(count)

    payload = [
        event.to_dict()
        for event in events
    ]

    output_path.write_text(
        json.dumps(
            payload,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    return output_path


def validate_transactions(
    input_path: Path,
    output_path: Path,
) -> Path:
    """Perform lightweight workflow-boundary validation."""
    payload = json.loads(
        input_path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(payload, list):
        raise ValueError(
            "transaction payload must be a list"
        )

    required_fields = {
        "transaction_id",
        "account_id",
        "amount",
        "currency",
        "merchant_category",
        "transaction_type",
        "timestamp",
        "country",
        "device_id",
    }

    validated: list[dict[str, Any]] = []

    for index, record in enumerate(payload):
        if not isinstance(record, dict):
            raise ValueError(
                f"record {index} must be an object"
            )

        missing = required_fields - record.keys()

        if missing:
            raise ValueError(
                f"record {index} missing fields: "
                f"{sorted(missing)}"
            )

        amount = float(record["amount"])

        if amount <= 0:
            raise ValueError(
                f"record {index} amount must be positive"
            )

        timestamp = datetime.fromisoformat(
            str(record["timestamp"])
        )

        if timestamp.tzinfo is None:
            raise ValueError(
                f"record {index} timestamp must be timezone-aware"
            )

        validated.append(record)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            validated,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path


def _build_spark_session():
    """
    Create Spark only when the processing task actually executes.

    PySpark is intentionally imported lazily so Airflow can parse the DAG
    without requiring Spark inside the Airflow scheduler environment.
    """
    from pyspark.sql import SparkSession

    return (
        SparkSession.builder
        .master("local[2]")
        .appName(
            "sprint09-day05-airflow-batch"
        )
        .config(
            "spark.sql.shuffle.partitions",
            "2",
        )
        .config(
            "spark.ui.enabled",
            "false",
        )
        .getOrCreate()
    )


def process_transactions(
    input_path: Path,
    output_path: Path,
) -> Path:
    """Run the account aggregation using Spark."""

    from streaming.spark.batch import aggregate_by_account
    from streaming.spark.schemas import TRANSACTION_SCHEMA

    payload = json.loads(
        input_path.read_text(
            encoding="utf-8",
        )
    )

    rows = []

    for record in payload:
        rows.append(
            (
                record["transaction_id"],
                record["account_id"],
                float(record["amount"]),
                record["currency"],
                record["merchant_category"],
                record["transaction_type"],
                datetime.fromisoformat(
                    record["timestamp"]
                ),
                record["country"],
                record["device_id"],
            )
        )

    spark = _build_spark_session()

    spark.sparkContext.setLogLevel("WARN")

    try:
        dataframe = spark.createDataFrame(
            rows,
            schema=TRANSACTION_SCHEMA,
        )

        summary = (
            aggregate_by_account(dataframe)
            .orderBy("account_id")
            .collect()
        )

        result = [
            row.asDict(recursive=True)
            for row in summary
        ]

    finally:
        spark.stop()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path


def generate_report(
    input_path: Path,
    output_path: Path,
) -> Path:
    """Generate a small workflow completion report."""
    account_summary = json.loads(
        input_path.read_text(
            encoding="utf-8",
        )
    )

    total_transactions = sum(
        int(row["transaction_count"])
        for row in account_summary
    )

    total_amount = round(
        sum(
            float(row["total_amount"])
            for row in account_summary
        ),
        2,
    )

    report = {
        "status": "completed",
        "account_count": len(account_summary),
        "transaction_count": total_transactions,
        "total_amount": total_amount,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path