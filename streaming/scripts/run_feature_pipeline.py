"""Run Sprint 9 Day 7 feature serving demonstration."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from streaming.features.engineering import (
    compute_account_features,
)
from streaming.features.repository import (
    build_store,
    get_historical_account_features,
    get_online_account_features,
)


FEATURE_DATA_PATH = Path(
    "feature_repo/data/account_features.parquet"
)


def build_transactions() -> pd.DataFrame:
    base = datetime(
        2026,
        9,
        18,
        6,
        0,
        tzinfo=timezone.utc,
    )

    return pd.DataFrame(
        [
            {
                "transaction_id": "txn-001",
                "account_id": "acc-001",
                "amount": 1000.0,
                "currency": "INR",
                "merchant_category": "grocery",
                "transaction_type": "purchase",
                "timestamp": base,
                "country": "IN",
                "device_id": "device-001",
            },
            {
                "transaction_id": "txn-002",
                "account_id": "acc-001",
                "amount": 5000.0,
                "currency": "INR",
                "merchant_category": "crypto",
                "transaction_type": "purchase",
                "timestamp": base + timedelta(minutes=15),
                "country": "SG",
                "device_id": "device-002",
            },
            {
                "transaction_id": "txn-003",
                "account_id": "acc-001",
                "amount": 2500.0,
                "currency": "INR",
                "merchant_category": "travel",
                "transaction_type": "purchase",
                "timestamp": base + timedelta(minutes=30),
                "country": "IN",
                "device_id": "device-001",
            },
            {
                "transaction_id": "txn-004",
                "account_id": "acc-002",
                "amount": 9000.0,
                "currency": "INR",
                "merchant_category": "gambling",
                "transaction_type": "purchase",
                "timestamp": base + timedelta(minutes=20),
                "country": "GB",
                "device_id": "device-003",
            },
        ]
    )


def main() -> None:
    feature_timestamp = datetime(
        2026,
        9,
        18,
        7,
        0,
        tzinfo=timezone.utc,
    )

    print("\n1. Build transactions")

    transactions = build_transactions()

    print(transactions)

    print("\n2. Compute offline features")

    features = compute_account_features(
        transactions,
        feature_timestamp=feature_timestamp,
    )

    print(features)

    print("\n3. Write offline feature data")

    FEATURE_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    features.to_parquet(
        FEATURE_DATA_PATH,
        index=False,
    )

    print(
        "Wrote:",
        FEATURE_DATA_PATH,
    )

    print("\n4. Open Feast FeatureStore")

    store = build_store()

    print("\n5. Historical feature retrieval")

    historical = get_historical_account_features(
        store,
        account_ids=[
            "acc-001",
            "acc-002",
        ],
        timestamps=[
            feature_timestamp,
            feature_timestamp,
        ],
    )

    print(historical)

    print(
        "\n6. Online retrieval happens "
        "after feast apply + materialization"
    )

    online = get_online_account_features(
        store,
        account_ids=[
            "acc-001",
            "acc-002",
        ],
    )

    print(online)


if __name__ == "__main__":
    main()