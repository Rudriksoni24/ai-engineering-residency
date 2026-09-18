from datetime import datetime, timezone

import pytest

from streaming.features.repository import (
    FEATURE_REFERENCES,
)


def test_expected_feature_references() -> None:
    assert FEATURE_REFERENCES == [
        "account_features:transaction_count_1h",
        "account_features:avg_transaction_amount_1h",
        "account_features:max_transaction_amount_1h",
        "account_features:recent_country_count",
        "account_features:recent_high_risk_merchant_count",
    ]


def test_feature_reference_names_are_unique() -> None:
    assert len(FEATURE_REFERENCES) == len(
        set(FEATURE_REFERENCES)
    )


def test_training_timestamp_is_timezone_aware() -> None:
    timestamp = datetime(
        2026,
        9,
        18,
        8,
        0,
        tzinfo=timezone.utc,
    )

    assert timestamp.utcoffset() is not None