from __future__ import annotations

from datetime import datetime, timezone, UTC
from pathlib import Path

import pytest

from streaming.contracts.transaction import (
    TransactionContract,
)
from streaming.lakehouse.delta_pipeline import (
    build_delta_spark_session,
    build_silver,
    contracts_to_dataframe,
    merge_transactions,
    read_delta,
    read_delta_version,
    table_history,
    write_bronze,
)


@pytest.fixture(scope="module")
def spark():
    session = build_delta_spark_session()

    session.sparkContext.setLogLevel(
        "ERROR"
    )

    yield session

    session.stop()


def transaction(
    transaction_id: str,
    *,
    amount: float = 1000.0,
) -> TransactionContract:
    return TransactionContract(
        transaction_id=transaction_id,
        account_id="acc-001",
        amount=amount,
        currency="inr",
        merchant_category="grocery",
        transaction_type="purchase",
        timestamp=datetime(
            2026,
            9,
            17,
            8,
            0,
            tzinfo=UTC,
        ),
        country="in",
        device_id="device-001",
    )


def test_contracts_to_dataframe(
    spark,
) -> None:
    dataframe = contracts_to_dataframe(
        spark,
        [
            transaction("txn-001"),
            transaction("txn-002"),
        ],
    )

    assert dataframe.count() == 2

    assert set(
        dataframe.columns
    ) == {
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


def test_bronze_append_and_time_travel(
    spark,
    tmp_path: Path,
) -> None:
    path = tmp_path / "bronze"

    first = contracts_to_dataframe(
        spark,
        [
            transaction("txn-001"),
            transaction("txn-002"),
        ],
    )

    write_bronze(
        first,
        path,
        mode="append",
    )

    assert read_delta(
        spark,
        path,
    ).count() == 2

    second = contracts_to_dataframe(
        spark,
        [
            transaction("txn-003"),
        ],
    )

    write_bronze(
        second,
        path,
        mode="append",
    )

    assert read_delta(
        spark,
        path,
    ).count() == 3

    assert read_delta_version(
        spark,
        path,
        0,
    ).count() == 2


def test_silver_deduplicates_transaction_id(
    spark,
) -> None:
    dataframe = contracts_to_dataframe(
        spark,
        [
            transaction("txn-001"),
            transaction("txn-001"),
            transaction("txn-002"),
        ],
    )

    silver = build_silver(
        dataframe
    )

    assert silver.count() == 2


def test_delta_merge_updates_existing_transaction(
    spark,
    tmp_path: Path,
) -> None:
    path = tmp_path / "merge-table"

    original = contracts_to_dataframe(
        spark,
        [
            transaction(
                "txn-001",
                amount=1000.0,
            )
        ],
    )

    write_bronze(
        original,
        path,
    )

    updated = contracts_to_dataframe(
        spark,
        [
            transaction(
                "txn-001",
                amount=2500.0,
            ),
            transaction(
                "txn-002",
                amount=500.0,
            ),
        ],
    )

    merge_transactions(
        spark,
        path,
        updated,
    )

    rows = {
        row.transaction_id: row.amount
        for row in (
            read_delta(
                spark,
                path,
            )
            .collect()
        )
    }

    assert rows == {
        "txn-001": 2500.0,
        "txn-002": 500.0,
    }


def test_delta_history_contains_multiple_versions(
    spark,
    tmp_path: Path,
) -> None:
    path = tmp_path / "history-table"

    write_bronze(
        contracts_to_dataframe(
            spark,
            [transaction("txn-001")],
        ),
        path,
    )

    write_bronze(
        contracts_to_dataframe(
            spark,
            [transaction("txn-002")],
        ),
        path,
    )

    versions = [
        row.version
        for row in (
            table_history(
                spark,
                path,
            )
            .select("version")
            .collect()
        )
    ]

    assert 0 in versions
    assert 1 in versions

    # uv run python -m streaming.scripts.run_delta_pipeline