"""Feast feature definitions for Sprint 9 Day 7."""

from datetime import timedelta

from feast import (
    Entity,
    FeatureView,
    Field,
    FileSource,
)
from feast.types import (
    Float64,
    Int64,
)

account = Entity(
    name="account",
    join_keys=["account_id"],
    description="Bank account",
)


account_features_source = FileSource(
    name="account_features_source",
    path="data/account_features.parquet",
    timestamp_field="event_timestamp",
)


account_features = FeatureView(
    name="account_features",
    entities=[account],
    ttl=timedelta(days=1),
    schema=[
        Field(
            name="transaction_count_1h",
            dtype=Int64,
        ),
        Field(
            name="avg_transaction_amount_1h",
            dtype=Float64,
        ),
        Field(
            name="max_transaction_amount_1h",
            dtype=Float64,
        ),
        Field(
            name="recent_country_count",
            dtype=Int64,
        ),
        Field(
            name="recent_high_risk_merchant_count",
            dtype=Int64,
        ),
    ],
    source=account_features_source,
    online=True,
)