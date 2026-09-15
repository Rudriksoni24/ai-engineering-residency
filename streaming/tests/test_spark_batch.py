from __future__ import annotations

import pytest
from pyspark.sql import SparkSession

from streaming.spark.batch import (
    add_country_mismatch_flag,
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


@pytest.fixture(scope="module")
def spark() -> SparkSession:
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("sprint09-day03-tests")
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
def transactions(
    spark: SparkSession,
):
    return spark.createDataFrame(
        transaction_rows(),
        schema=TRANSACTION_SCHEMA,
    )


@pytest.fixture()
def accounts(
    spark: SparkSession,
):
    return spark.createDataFrame(
        sample_accounts(),
        schema=ACCOUNT_SCHEMA,
    )


def test_transaction_schema_is_explicit(
    transactions,
) -> None:
    assert transactions.columns == [
        "transaction_id",
        "account_id",
        "amount",
        "currency",
        "merchant_category",
        "transaction_type",
        "timestamp",
        "country",
        "device_id",
    ]


def test_suspicious_transaction_filter(
    transactions,
) -> None:
    result = (
        filter_suspicious_transactions(
            transactions,
            amount_threshold=10_000.0,
        )
        .select("transaction_id")
        .orderBy("transaction_id")
        .collect()
    )

    transaction_ids = [
        row.transaction_id
        for row in result
    ]

    assert transaction_ids == [
        "txn-002",
        "txn-004",
        "txn-006",
    ]


def test_account_aggregation(
    transactions,
) -> None:
    result = {
        row.account_id: row
        for row in (
            aggregate_by_account(
                transactions
            )
            .collect()
        )
    }

    assert result["acc-001"].transaction_count == 2
    assert result["acc-001"].total_amount == 16_200.0
    assert result["acc-001"].average_amount == 8100.0
    assert result["acc-001"].max_amount == 15_000.0

    assert result["acc-002"].transaction_count == 2
    assert result["acc-002"].total_amount == 24_850.0

    assert result["acc-003"].transaction_count == 2
    assert result["acc-003"].total_amount == 37_000.0


def test_merchant_category_aggregation(
    transactions,
) -> None:
    result = {
        row.merchant_category: row
        for row in (
            aggregate_by_merchant_category(
                transactions
            )
            .collect()
        )
    }

    electronics = result["electronics"]

    assert electronics.transaction_count == 2
    assert electronics.total_amount == 47_000.0
    assert electronics.average_amount == 23_500.0


def test_global_statistics(
    transactions,
) -> None:
    result = (
        calculate_global_statistics(
            transactions
        )
        .collect()[0]
    )

    assert result.transaction_count == 6
    assert result.total_amount == 78_050.0
    assert result.min_amount == 850.0
    assert result.max_amount == 32_000.0


def test_account_metadata_join(
    transactions,
    accounts,
) -> None:
    result = (
        build_processed_transactions(
            transactions,
            accounts,
        )
        .filter(
            "transaction_id = 'txn-001'"
        )
        .collect()[0]
    )

    assert result.account_id == "acc-001"
    assert result.customer_segment == "premium"
    assert result.home_country == "IN"


def test_country_mismatch_flag(
    transactions,
    accounts,
) -> None:
    result = {
        row.transaction_id: row.country_mismatch
        for row in (
            build_processed_transactions(
                transactions,
                accounts,
            )
            .select(
                "transaction_id",
                "country_mismatch",
            )
            .collect()
        )
    }

    assert result["txn-001"] is False
    assert result["txn-004"] is True
    assert result["txn-006"] is True


def test_native_expression_preserves_row_count(
    transactions,
    accounts,
) -> None:
    enriched = transactions.join(
        accounts,
        on="account_id",
        how="left",
    )

    result = add_country_mismatch_flag(
        enriched
    )

    assert result.count() == transactions.count()