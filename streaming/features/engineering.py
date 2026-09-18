"""Feature engineering for Sprint 9 Day 7."""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

HIGH_RISK_MERCHANT_CATEGORIES = {
    "crypto",
    "gambling",
}


def compute_account_features(
    transactions: pd.DataFrame,
    *,
    feature_timestamp: datetime,
    window: timedelta = timedelta(hours=1),
) -> pd.DataFrame:
    """Compute account features using only data known by feature_timestamp."""

    required = {
        "account_id",
        "amount",
        "merchant_category",
        "timestamp",
        "country",
    }

    missing = required - set(transactions.columns)

    if missing:
        raise ValueError(
            f"missing transaction columns: {sorted(missing)}"
        )

    frame = transactions.copy()

    frame["timestamp"] = pd.to_datetime(
        frame["timestamp"],
        utc=True,
    )

    timestamp = pd.Timestamp(feature_timestamp)

    if timestamp.tzinfo is None:
        raise ValueError(
            "feature_timestamp must be timezone-aware"
        )

    timestamp = timestamp.tz_convert("UTC")

    window_start = timestamp - window

    eligible = frame[
        (frame["timestamp"] <= timestamp)
        & (frame["timestamp"] > window_start)
    ].copy()

    if eligible.empty:
        return pd.DataFrame(
            columns=[
                "account_id",
                "event_timestamp",
                "transaction_count_1h",
                "avg_transaction_amount_1h",
                "max_transaction_amount_1h",
                "recent_country_count",
                "recent_high_risk_merchant_count",
            ]
        )

    eligible["is_high_risk_merchant"] = (
        eligible["merchant_category"]
        .isin(HIGH_RISK_MERCHANT_CATEGORIES)
        .astype(int)
    )

    result = (
        eligible.groupby(
            "account_id",
            as_index=False,
        )
        .agg(
            transaction_count_1h=(
                "amount",
                "size",
            ),
            avg_transaction_amount_1h=(
                "amount",
                "mean",
            ),
            max_transaction_amount_1h=(
                "amount",
                "max",
            ),
            recent_country_count=(
                "country",
                "nunique",
            ),
            recent_high_risk_merchant_count=(
                "is_high_risk_merchant",
                "sum",
            ),
        )
    )

    result["event_timestamp"] = timestamp

    return result[
        [
            "account_id",
            "event_timestamp",
            "transaction_count_1h",
            "avg_transaction_amount_1h",
            "max_transaction_amount_1h",
            "recent_country_count",
            "recent_high_risk_merchant_count",
        ]
    ]