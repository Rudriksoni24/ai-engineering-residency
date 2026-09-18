"""Delta Lake pipeline operations for Sprint 9 Day 6."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from delta import configure_spark_with_delta_pip
from delta.tables import DeltaTable
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from streaming.contracts.transaction import (
    TransactionContract,
)
from streaming.spark.batch import aggregate_by_account
from streaming.spark.schemas import TRANSACTION_SCHEMA


def build_delta_spark_session() -> SparkSession:
    """Build a local SparkSession configured for Delta Lake."""

    builder = (
        SparkSession.builder
        .master("local[2]")
        .appName("sprint09-day06-delta")
        .config(
            "spark.sql.extensions",
            "io.delta.sql.DeltaSparkSessionExtension",
        )
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config(
            "spark.sql.shuffle.partitions",
            "2",
        )
        .config(
            "spark.ui.enabled",
            "false",
        )
    )

    return configure_spark_with_delta_pip(
        builder
    ).getOrCreate()


def contracts_to_dataframe(
    spark: SparkSession,
    contracts: Iterable[TransactionContract],
) -> DataFrame:
    """Convert validated contracts into an explicit Spark DataFrame."""

    rows = [
        (
            contract.transaction_id,
            contract.account_id,
            contract.amount,
            contract.currency,
            contract.merchant_category,
            contract.transaction_type,
            contract.timestamp,
            contract.country,
            contract.device_id,
        )
        for contract in contracts
    ]

    return spark.createDataFrame(
        rows,
        schema=TRANSACTION_SCHEMA,
    )


def write_bronze(
    dataframe: DataFrame,
    path: Path,
    *,
    mode: str = "append",
) -> None:
    """Persist validated transaction records to Bronze Delta."""

    (
        dataframe.write
        .format("delta")
        .mode(mode)
        .save(str(path))
    )


def build_silver(
    bronze_dataframe: DataFrame,
) -> DataFrame:
    """Normalize and deduplicate transaction records."""

    return (
        bronze_dataframe
        .filter(F.col("amount") > 0)
        .withColumn(
            "currency",
            F.upper(F.col("currency")),
        )
        .withColumn(
            "country",
            F.upper(F.col("country")),
        )
        .dropDuplicates(
            ["transaction_id"]
        )
    )


def write_silver(
    dataframe: DataFrame,
    path: Path,
) -> None:
    """Write the current normalized Silver dataset."""

    (
        dataframe.write
        .format("delta")
        .mode("overwrite")
        .save(str(path))
    )


def build_gold(
    silver_dataframe: DataFrame,
) -> DataFrame:
    """Build account-level Gold aggregates."""

    return aggregate_by_account(
        silver_dataframe
    )


def write_gold(
    dataframe: DataFrame,
    path: Path,
) -> None:
    """Write Gold analytical output."""

    (
        dataframe.write
        .format("delta")
        .mode("overwrite")
        .save(str(path))
    )


def merge_transactions(
    spark: SparkSession,
    target_path: Path,
    source_dataframe: DataFrame,
) -> None:
    """
    Upsert transactions using transaction_id as business identity.

    Matching rows are updated and new rows are inserted.
    """

    target = DeltaTable.forPath(
        spark,
        str(target_path),
    )

    (
        target.alias("target")
        .merge(
            source_dataframe.alias("source"),
            (
                "target.transaction_id "
                "= source.transaction_id"
            ),
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )


def read_delta(
    spark: SparkSession,
    path: Path,
) -> DataFrame:
    """Read the current Delta table version."""

    return (
        spark.read
        .format("delta")
        .load(str(path))
    )


def read_delta_version(
    spark: SparkSession,
    path: Path,
    version: int,
) -> DataFrame:
    """Read a specific historical Delta version."""

    return (
        spark.read
        .format("delta")
        .option(
            "versionAsOf",
            version,
        )
        .load(str(path))
    )


def table_history(
    spark: SparkSession,
    path: Path,
) -> DataFrame:
    """Return Delta transaction history."""

    return (
        DeltaTable
        .forPath(
            spark,
            str(path),
        )
        .history()
    )