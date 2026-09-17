from __future__ import annotations

from datetime import datetime

import pytest
from pyspark.sql import SparkSession

from streaming.spark.structured_streaming import (
    add_high_value_flag,
    build_transaction_stream,
    build_windowed_account_summary,
    filter_valid_transactions,
    parse_kafka_transactions,
)


@pytest.fixture(scope="module")
def spark() -> SparkSession:
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("sprint09-day04-tests")
        .config(
            "spark.ui.enabled",
            "false",
        )
        .config(
            "spark.sql.shuffle.partitions",
            "2",
        )
        .getOrCreate()
    )

    session.sparkContext.setLogLevel("ERROR")

    yield session

    session.stop()


@pytest.fixture()
def kafka_dataframe(
    spark: SparkSession,
):
    event = """
    {
      "transaction_id": "txn-stream-001",
      "account_id": "acc-001",
      "amount": 15000.0,
      "currency": "INR",
      "merchant_category": "electronics",
      "transaction_type": "purchase",
      "timestamp": "2026-09-15T08:00:00+00:00",
      "country": "IN",
      "device_id": "device-001"
    }
    """

    return spark.createDataFrame(
        [
            (
                b"acc-001",
                event.encode("utf-8"),
                "transactions",
                0,
                42,
                datetime(
                    2026,
                    9,
                    15,
                    8,
                    0,
                ),
            )
        ],
        schema="""
            key binary,
            value binary,
            topic string,
            partition integer,
            offset long,
            timestamp timestamp
        """,
    )


def test_parse_kafka_transaction(
    kafka_dataframe,
) -> None:
    row = (
        parse_kafka_transactions(
            kafka_dataframe
        )
        .collect()[0]
    )

    assert row.kafka_key == "acc-001"
    assert row.kafka_topic == "transactions"
    assert row.kafka_partition == 0
    assert row.kafka_offset == 42

    assert row.transaction_id == "txn-stream-001"
    assert row.account_id == "acc-001"
    assert row.amount == 15_000.0
    assert row.currency == "INR"


def test_invalid_transaction_is_filtered(
    spark: SparkSession,
) -> None:
    dataframe = spark.createDataFrame(
        [
            (
                "txn-valid",
                "acc-001",
                100.0,
                "INR",
                datetime(
                    2026,
                    9,
                    15,
                    8,
                    0,
                ),
            ),
            (
                "txn-invalid",
                "acc-002",
                -10.0,
                "INR",
                datetime(
                    2026,
                    9,
                    15,
                    8,
                    1,
                ),
            ),
        ],
        schema="""
            transaction_id string,
            account_id string,
            amount double,
            currency string,
            event_timestamp timestamp
        """,
    )

    result = (
        filter_valid_transactions(
            dataframe
        )
        .collect()
    )

    assert len(result) == 1
    assert result[0].transaction_id == "txn-valid"


def test_high_value_flag(
    spark: SparkSession,
) -> None:
    dataframe = spark.createDataFrame(
        [
            ("txn-001", 9999.0),
            ("txn-002", 10000.0),
            ("txn-003", 25000.0),
        ],
        schema="""
            transaction_id string,
            amount double
        """,
    )

    result = {
        row.transaction_id: row.is_high_value
        for row in (
            add_high_value_flag(
                dataframe,
                threshold=10_000.0,
            )
            .collect()
        )
    }

    assert result == {
        "txn-001": False,
        "txn-002": True,
        "txn-003": True,
    }


def test_complete_transaction_pipeline(
    kafka_dataframe,
) -> None:
    result = (
        build_transaction_stream(
            kafka_dataframe
        )
        .collect()[0]
    )

    assert result.transaction_id == "txn-stream-001"
    assert result.is_high_value is True


def test_windowed_account_summary(
    spark: SparkSession,
) -> None:
    dataframe = spark.createDataFrame(
        [
            (
                "acc-001",
                100.0,
                datetime(
                    2026,
                    9,
                    15,
                    8,
                    1,
                ),
            ),
            (
                "acc-001",
                200.0,
                datetime(
                    2026,
                    9,
                    15,
                    8,
                    2,
                ),
            ),
            (
                "acc-002",
                500.0,
                datetime(
                    2026,
                    9,
                    15,
                    8,
                    3,
                ),
            ),
        ],
        schema="""
            account_id string,
            amount double,
            event_timestamp timestamp
        """,
    )

    result = (
        build_windowed_account_summary(
            dataframe,
            watermark_delay="10 minutes",
            window_duration="5 minutes",
        )
        .collect()
    )

    by_account = {
        row.account_id: row
        for row in result
    }

    assert by_account["acc-001"].transaction_count == 2
    assert by_account["acc-001"].total_amount == 300.0
    assert by_account["acc-001"].max_amount == 200.0

    assert by_account["acc-002"].transaction_count == 1
    assert by_account["acc-002"].total_amount == 500.0