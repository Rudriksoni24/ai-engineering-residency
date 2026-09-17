"""Structured Streaming transformations for transaction events."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from streaming.spark.schemas import TRANSACTION_SCHEMA


def parse_kafka_transactions(
    kafka_dataframe: DataFrame,
) -> DataFrame:
    """
    Parse Kafka JSON values into typed transaction columns.

    Kafka metadata is retained so transport identity remains observable.
    """
    decoded = kafka_dataframe.select(
        F.col("key").cast("string").alias("kafka_key"),
        F.col("value").cast("string").alias("json_value"),
        F.col("topic").alias("kafka_topic"),
        F.col("partition").alias("kafka_partition"),
        F.col("offset").alias("kafka_offset"),
        F.col("timestamp").alias("kafka_timestamp"),
    )

    parsed = decoded.withColumn(
        "transaction",
        F.from_json(
            F.col("json_value"),
            TRANSACTION_SCHEMA,
        ),
    )

    return parsed.select(
        "kafka_key",
        "kafka_topic",
        "kafka_partition",
        "kafka_offset",
        "kafka_timestamp",
        F.col("transaction.transaction_id").alias(
            "transaction_id"
        ),
        F.col("transaction.account_id").alias(
            "account_id"
        ),
        F.col("transaction.amount").alias("amount"),
        F.col("transaction.currency").alias("currency"),
        F.col(
            "transaction.merchant_category"
        ).alias("merchant_category"),
        F.col(
            "transaction.transaction_type"
        ).alias("transaction_type"),
        F.col("transaction.timestamp").alias(
            "event_timestamp"
        ),
        F.col("transaction.country").alias("country"),
        F.col("transaction.device_id").alias("device_id"),
    )


def filter_valid_transactions(
    dataframe: DataFrame,
) -> DataFrame:
    """
    Apply lightweight Day 4 validation.

    Full reusable application contracts belong to Day 6.
    """
    return dataframe.filter(
        F.col("transaction_id").isNotNull()
        & F.col("account_id").isNotNull()
        & F.col("event_timestamp").isNotNull()
        & F.col("amount").isNotNull()
        & (F.col("amount") > 0)
        & F.col("currency").isNotNull()
    )


def add_high_value_flag(
    dataframe: DataFrame,
    *,
    threshold: float = 10_000.0,
) -> DataFrame:
    """Add a simple learning-oriented high-value flag."""
    return dataframe.withColumn(
        "is_high_value",
        F.col("amount") >= F.lit(threshold),
    )


def build_transaction_stream(
    kafka_dataframe: DataFrame,
) -> DataFrame:
    """Build the parsed and validated transaction stream."""
    return (
        parse_kafka_transactions(kafka_dataframe)
        .transform(filter_valid_transactions)
        .transform(add_high_value_flag)
    )


def build_windowed_account_summary(
    dataframe: DataFrame,
    *,
    watermark_delay: str = "10 minutes",
    window_duration: str = "5 minutes",
) -> DataFrame:
    """
    Aggregate transaction activity using authoritative event time.

    This operation is stateful when used with a streaming DataFrame.
    """
    return (
        dataframe
        .withWatermark(
            "event_timestamp",
            watermark_delay,
        )
        .groupBy(
            F.window(
                F.col("event_timestamp"),
                window_duration,
            ),
            F.col("account_id"),
        )
        .agg(
            F.count("*").alias("transaction_count"),
            F.round(
                F.sum("amount"),
                2,
            ).alias("total_amount"),
            F.round(
                F.max("amount"),
                2,
            ).alias("max_amount"),
        )
    )