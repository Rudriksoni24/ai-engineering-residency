from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

ENGINEERED_COLUMNS = [
    "transaction_amount",
    "transaction_type",
    "account_age_days",
    "transaction_hour",
    "merchant_category",
    "country_risk",
    "previous_transaction_count",
    "account_balance",
    "amount_log",
    "is_night_transaction",
    "amount_to_balance_ratio",
    "account_age_bucket",
    "transaction_velocity",
    "high_risk_category",
]


class FraudFeatureTransformer(
    BaseEstimator,
    TransformerMixin,
):
    """Create deterministic row-level fraud features.

    The transformer intentionally uses only information already available
    within each row.

    It does not learn dataset-wide statistics, making the derived-feature
    stage stateless and leakage-safe for Day 2.
    """

    REQUIRED_COLUMNS = {  # noqa: RUF012
        "transaction_amount",
        "transaction_type",
        "account_age_days",
        "transaction_hour",
        "merchant_category",
        "country_risk",
        "previous_transaction_count",
        "account_balance",
    }

    def fit(
        self,
        X: pd.DataFrame,
        y: object = None,
    ) -> FraudFeatureTransformer:
        self._validate_input(X)
        return self

    def transform(
        self,
        X: pd.DataFrame,
    ) -> pd.DataFrame:
        self._validate_input(X)

        result = X.copy()

        amount = pd.to_numeric(
            result["transaction_amount"],
            errors="coerce",
        )

        balance = pd.to_numeric(
            result["account_balance"],
            errors="coerce",
        )

        hour = pd.to_numeric(
            result["transaction_hour"],
            errors="coerce",
        )

        account_age = pd.to_numeric(
            result["account_age_days"],
            errors="coerce",
        )

        previous_count = pd.to_numeric(
            result["previous_transaction_count"],
            errors="coerce",
        )

        result["amount_log"] = np.log1p(
            amount.clip(lower=0)
        )

        result["is_night_transaction"] = (
            (hour <= 4) | (hour >= 23)
        ).astype(float)

        safe_balance = balance.replace(
            0,
            np.nan,
        )

        result["amount_to_balance_ratio"] = (
            amount / safe_balance
        )

        result["account_age_bucket"] = pd.cut(
            account_age,
            bins=[
                -np.inf,
                180,
                365,
                1_095,
                np.inf,
            ],
            labels=[
                "new",
                "young",
                "established",
                "mature",
            ],
        ).astype("object")

        # This is deliberately simple on Day 2.
        #
        # We use an existing row-level count as a proxy rather than calculating
        # history across the entire dataset, which could introduce temporal
        # leakage.
        result["transaction_velocity"] = (
            previous_count
        )

        result["high_risk_category"] = (
            result["merchant_category"]
            .isin(
                [
                    "electronics",
                    "travel",
                ]
            )
            .astype(float)
        )

        return result[ENGINEERED_COLUMNS]

    def _validate_input(
        self,
        X: pd.DataFrame,
    ) -> None:
        if not isinstance(X, pd.DataFrame):
            raise TypeError(
                "FraudFeatureTransformer requires a pandas DataFrame"
            )

        missing = self.REQUIRED_COLUMNS.difference(
            X.columns
        )

        if missing:
            raise ValueError(
                "Feature input is missing required columns: "
                f"{sorted(missing)}"
            )