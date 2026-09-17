"""Run the Sprint 9 Day 4 Kafka-to-Spark streaming pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from pyspark.sql import SparkSession

from streaming.spark.structured_streaming import (
    build_transaction_stream,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Consume transaction events from Kafka using "
            "Spark Structured Streaming."
        )
    )

    parser.add_argument(
        "--bootstrap-servers",
        default="localhost:9092",
    )

    parser.add_argument(
        "--topic",
        default="transactions",
    )

    parser.add_argument(
        "--checkpoint",
        default=(
            "artifacts/sprint09/day04/"
            "transaction-console-checkpoint"
        ),
    )

    return parser.parse_args()


def build_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .master("local[2]")
        .appName(
            "sprint09-day04-structured-streaming"
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


def main() -> None:
    args = parse_args()

    checkpoint = Path(args.checkpoint)

    checkpoint.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    spark = build_spark_session()

    spark.sparkContext.setLogLevel("WARN")

    kafka_stream = (
        spark.readStream
        .format("kafka")
        .option(
            "kafka.bootstrap.servers",
            args.bootstrap_servers,
        )
        .option(
            "subscribe",
            args.topic,
        )
        .option(
            "startingOffsets",
            "earliest",
        )
        .load()
    )

    transactions = build_transaction_stream(
        kafka_stream
    )

    output = transactions.select(
        "transaction_id",
        "account_id",
        "amount",
        "currency",
        "merchant_category",
        "transaction_type",
        "event_timestamp",
        "country",
        "device_id",
        "is_high_value",
        "kafka_partition",
        "kafka_offset",
    )

    query = (
        output.writeStream
        .format("console")
        .outputMode("append")
        .option(
            "truncate",
            "false",
        )
        .option(
            "checkpointLocation",
            str(checkpoint),
        )
        .trigger(
            processingTime="5 seconds",
        )
        .start()
    )

    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print(
            "\nStopping Structured Streaming query..."
        )
    finally:
        query.stop()
        spark.stop()


if __name__ == "__main__":
    main()

    #PYSPARK_SUBMIT_ARGS="--packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0 pyspark-shell" \
# uv run python -m streaming.scripts.run_structured_streaming