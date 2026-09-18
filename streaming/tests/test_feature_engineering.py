from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from streaming.features.engineering import (
    compute_account_features,
)


BASE = datetime(
    2026,
    9,
    18,
    8,
    0,
    tzinfo=timezone.utc,
)


def transactions() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "account_id": "acc-001",
                "amount": 1000.0,
                "merchant_category": "grocery",
                "timestamp": BASE,
                "country": "IN",
            },
            {
                "account_id": "acc-001",
                "amount": 3000.0,
                "merchant_category": "crypto",
                "timestamp": BASE
                + timedelta(minutes=10),
                "country": "SG",
            },
            {
                "account_id": "acc-002",
                "amount": 500.0,
                "merchant_category": "fuel",
                "timestamp": BASE
                + timedelta(minutes=20),
                "country": "IN",
            },
        ]
    )


def test_computes_account_features() -> None:
    result = compute_account_features(
        transactions(),
        feature_timestamp=BASE
        + timedelta(minutes=30),
    )

    account = (
        result
        .set_index("account_id")
        .loc["acc-001"]
    )

    assert account["transaction_count_1h"] == 2
    assert account["avg_transaction_amount_1h"] == 2000.0
    assert account["max_transaction_amount_1h"] == 3000.0
    assert account["recent_country_count"] == 2
    assert account["recent_high_risk_merchant_count"] == 1


def test_future_transactions_are_excluded() -> None:
    result = compute_account_features(
        transactions(),
        feature_timestamp=BASE
        + timedelta(minutes=5),
    )

    account = (
        result
        .set_index("account_id")
        .loc["acc-001"]
    )

    assert account["transaction_count_1h"] == 1
    assert account["max_transaction_amount_1h"] == 1000.0


def test_old_transactions_are_excluded() -> None:
    frame = transactions()

    old = pd.DataFrame(
        [
            {
                "account_id": "acc-001",
                "amount": 99999.0,
                "merchant_category": "crypto",
                "timestamp": BASE
                - timedelta(hours=2),
                "country": "US",
            }
        ]
    )

    frame = pd.concat(
        [frame, old],
        ignore_index=True,
    )

    result = compute_account_features(
        frame,
        feature_timestamp=BASE
        + timedelta(minutes=30),
    )

    account = (
        result
        .set_index("account_id")
        .loc["acc-001"]
    )

    assert account["transaction_count_1h"] == 2
    assert account["max_transaction_amount_1h"] == 3000.0


def test_naive_feature_timestamp_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        compute_account_features(
            transactions(),
            feature_timestamp=datetime(
                2026,
                9,
                18,
                8,
                30,
            ),
        )


def test_missing_columns_rejected() -> None:
    frame = transactions().drop(
        columns=["country"]
    )

    with pytest.raises(
        ValueError,
        match="missing transaction columns",
    ):
        compute_account_features(
            frame,
            feature_timestamp=BASE,
        )