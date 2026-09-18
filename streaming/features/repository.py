"""Helpers around the local Feast feature repository."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from feast import FeatureStore


FEATURE_REPO = Path("feature_repo")


FEATURE_REFERENCES = [
    "account_features:transaction_count_1h",
    "account_features:avg_transaction_amount_1h",
    "account_features:max_transaction_amount_1h",
    "account_features:recent_country_count",
    "account_features:recent_high_risk_merchant_count",
]


def build_store(
    repo_path: Path = FEATURE_REPO,
) -> FeatureStore:
    return FeatureStore(
        repo_path=str(repo_path),
    )


def get_historical_account_features(
    store: FeatureStore,
    *,
    account_ids: list[str],
    timestamps: list[datetime],
) -> pd.DataFrame:
    if len(account_ids) != len(timestamps):
        raise ValueError(
            "account_ids and timestamps must have equal length"
        )

    entity_df = pd.DataFrame(
        {
            "account_id": account_ids,
            "event_timestamp": pd.to_datetime(
                timestamps,
                utc=True,
            ),
        }
    )

    return (
        store.get_historical_features(
            entity_df=entity_df,
            features=FEATURE_REFERENCES,
        )
        .to_df()
    )


def get_online_account_features(
    store: FeatureStore,
    *,
    account_ids: list[str],
) -> dict:
    return store.get_online_features(
        features=FEATURE_REFERENCES,
        entity_rows=[
            {
                "account_id": account_id,
            }
            for account_id in account_ids
        ],
    ).to_dict()