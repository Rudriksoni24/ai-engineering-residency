"""Run Sprint 9 Day 3 PySpark batch processing demo."""

from __future__ import annotations

from pyspark.sql import SparkSession

from streaming.spark.batch import (
    aggregate_by_account,
    aggregate_by_merchant_category,
    build_processed_transactions,
    calculate_global_statistics,
    filter_suspicious_transactions,
)
from streaming.spark.sample_data import (
    sample_accounts,
    transaction_rows,
)
from streaming.spark.schemas import (
    ACCOUNT_SCHEMA,
    TRANSACTION_SCHEMA,
)


def build_spark_session() -> SparkSession:
    """Create a lightweight local Spark session."""
    return (
        SparkSession.builder
        .master("local[2]")
        .appName("sprint09-day03-pyspark")
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


def main() -> None:
    spark = build_spark_session()

    spark.sparkContext.setLogLevel("WARN")

    try:
        transactions = spark.createDataFrame(
            transaction_rows(),
            schema=TRANSACTION_SCHEMA,
        )

        accounts = spark.createDataFrame(
            sample_accounts(),
            schema=ACCOUNT_SCHEMA,
        )

        print("\n=== Spark Environment ===")
        print(f"Version: {spark.version}")
        print(f"Master: {spark.sparkContext.master}")
        print(
            "Shuffle partitions:",
            spark.conf.get(
                "spark.sql.shuffle.partitions"
            ),
        )

        print("\n=== Transaction Schema ===")
        transactions.printSchema()

        print("\n=== Raw Transactions ===")
        transactions.show(
            truncate=False
        )

        print("\n=== Physical Partitions ===")
        print(
            "Transaction partitions:",
            transactions.rdd.getNumPartitions(),
        )

        print("\n=== Suspicious Transactions ===")

        suspicious = (
            filter_suspicious_transactions(
                transactions,
                amount_threshold=10_000.0,
            )
        )

        suspicious.show(
            truncate=False
        )

        print("\n=== Account Aggregation ===")

        account_summary = (
            aggregate_by_account(
                transactions
            )
            .orderBy("account_id")
        )

        account_summary.show(
            truncate=False
        )

        print("\n=== Merchant Category Aggregation ===")

        merchant_summary = (
            aggregate_by_merchant_category(
                transactions
            )
            .orderBy("merchant_category")
        )

        merchant_summary.show(
            truncate=False
        )

        print("\n=== Global Statistics ===")

        calculate_global_statistics(
            transactions
        ).show(
            truncate=False
        )

        print("\n=== Enriched Transactions ===")

        processed = (
            build_processed_transactions(
                transactions,
                accounts,
            )
            .orderBy("transaction_id")
        )

        processed.show(
            truncate=False
        )

        print("\n=== Logical / Physical Plan ===")

        account_summary.explain(
            mode="formatted"
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()

    # uv run python -m streaming.scripts.run_spark_batch