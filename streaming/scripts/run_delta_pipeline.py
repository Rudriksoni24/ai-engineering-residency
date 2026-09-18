"""Run the Sprint 9 Day 6 local lakehouse pipeline."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path

from streaming.contracts.transaction import (
    TransactionContract,
)
from streaming.lakehouse.delta_pipeline import (
    build_delta_spark_session,
    build_gold,
    build_silver,
    contracts_to_dataframe,
    merge_transactions,
    read_delta,
    read_delta_version,
    table_history,
    write_bronze,
    write_gold,
    write_silver,
)


def build_transactions() -> list[TransactionContract]:
    base = datetime(
        2026,
        9,
        17,
        8,
        0,
        tzinfo=UTC,
    )

    return [
        TransactionContract(
            transaction_id="txn-001",
            account_id="acc-001",
            amount=1200.0,
            currency="inr",
            merchant_category="grocery",
            transaction_type="purchase",
            timestamp=base,
            country="in",
            device_id="device-001",
        ),
        TransactionContract(
            transaction_id="txn-002",
            account_id="acc-001",
            amount=15000.0,
            currency="INR",
            merchant_category="electronics",
            transaction_type="purchase",
            timestamp=base + timedelta(minutes=5),
            country="IN",
            device_id="device-001",
        ),
        TransactionContract(
            transaction_id="txn-003",
            account_id="acc-002",
            amount=850.0,
            currency="INR",
            merchant_category="fuel",
            transaction_type="purchase",
            timestamp=base + timedelta(minutes=10),
            country="IN",
            device_id="device-002",
        ),
    ]


def main() -> None:
    root = Path(
        "artifacts/sprint09/day06"
    )

    bronze_path = root / "bronze_transactions"
    silver_path = root / "silver_transactions"
    gold_path = root / "gold_account_summary"

    if root.exists():
        shutil.rmtree(root)

    spark = build_delta_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    try:
        print("\n1. Validate transaction contracts")

        contracts = build_transactions()

        for contract in contracts:
            print(
                contract.transaction_id,
                contract.currency,
                contract.timestamp.isoformat(),
            )

        print("\n2. Build Spark DataFrame")

        dataframe = contracts_to_dataframe(
            spark,
            contracts,
        )

        dataframe.show(
            truncate=False
        )

        print("\n3. Write Bronze Delta")

        write_bronze(
            dataframe,
            bronze_path,
            mode="append",
        )

        bronze = read_delta(
            spark,
            bronze_path,
        )

        print(
            "Bronze count:",
            bronze.count(),
        )

        print("\n4. Build Silver")

        silver = build_silver(
            bronze
        )

        write_silver(
            silver,
            silver_path,
        )

        print(
            "Silver count:",
            read_delta(
                spark,
                silver_path,
            ).count(),
        )

        print("\n5. Build Gold")

        gold = build_gold(
            silver
        )

        write_gold(
            gold,
            gold_path,
        )

        read_delta(
            spark,
            gold_path,
        ).show(
            truncate=False
        )

        print("\n6. Bronze history")

        table_history(
            spark,
            bronze_path,
        ).select(
            "version",
            "timestamp",
            "operation",
        ).show(
            truncate=False
        )

        print("\n7. Append another transaction")

        new_contract = TransactionContract(
            transaction_id="txn-004",
            account_id="acc-002",
            amount=24000.0,
            currency="INR",
            merchant_category="travel",
            transaction_type="purchase",
            timestamp=datetime(
                2026,
                9,
                17,
                8,
                15,
                tzinfo=UTC,
            ),
            country="SG",
            device_id="device-003",
        )

        new_dataframe = contracts_to_dataframe(
            spark,
            [new_contract],
        )

        write_bronze(
            new_dataframe,
            bronze_path,
            mode="append",
        )

        current = read_delta(
            spark,
            bronze_path,
        )

        print(
            "Current Bronze count:",
            current.count(),
        )

        print("\n8. Time travel to version 0")

        version_zero = read_delta_version(
            spark,
            bronze_path,
            0,
        )

        print(
            "Version 0 count:",
            version_zero.count(),
        )

        print("\n9. MERGE demonstration")

        updated_contract = TransactionContract(
            transaction_id="txn-004",
            account_id="acc-002",
            amount=25000.0,
            currency="INR",
            merchant_category="travel",
            transaction_type="purchase",
            timestamp=datetime(
                2026,
                9,
                17,
                8,
                15,
                tzinfo=UTC,
            ),
            country="SG",
            device_id="device-003",
        )

        update_dataframe = contracts_to_dataframe(
            spark,
            [updated_contract],
        )

        merge_transactions(
            spark,
            bronze_path,
            update_dataframe,
        )

        (
            read_delta(
                spark,
                bronze_path,
            )
            .filter(
                "transaction_id = 'txn-004'"
            )
            .show(
                truncate=False
            )
        )

        print("\n10. Final Bronze history")

        table_history(
            spark,
            bronze_path,
        ).select(
            "version",
            "operation",
        ).show(
            truncate=False
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()