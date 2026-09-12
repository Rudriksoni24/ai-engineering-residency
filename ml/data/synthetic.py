from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "transaction_amount",
    "transaction_type",
    "account_age_days",
    "transaction_hour",
    "merchant_category",
    "country_risk",
    "previous_transaction_count",
    "account_balance",
]

TARGET_COLUMN = "fraud_label"


def generate_synthetic_transactions(
    *,
    n_samples: int = 3_000,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Generate a deterministic synthetic banking transaction dataset.

    The generator intentionally creates an imbalanced binary classification
    problem resembling fraud detection without containing PII.

    Args:
        n_samples: Number of transaction rows to generate.
        random_seed: Seed controlling every stochastic operation.

    Returns:
        A DataFrame containing raw features and fraud_label.

    Raises:
        ValueError: If n_samples is too small for a meaningful dataset.
    """
    if n_samples < 100:
        raise ValueError("n_samples must be at least 100")

    rng = np.random.default_rng(random_seed)

    transaction_amount = rng.lognormal(
        mean=4.7,
        sigma=1.0,
        size=n_samples,
    )

    transaction_type = rng.choice(
        ["card", "transfer", "cash_withdrawal", "bill_payment"],
        size=n_samples,
        p=[0.45, 0.25, 0.15, 0.15],
    )

    account_age_days = rng.integers(
        low=30,
        high=3_650,
        size=n_samples,
    )

    transaction_hour = rng.integers(
        low=0,
        high=24,
        size=n_samples,
    )

    merchant_category = rng.choice(
        [
            "grocery",
            "electronics",
            "travel",
            "fuel",
            "utilities",
            "other",
        ],
        size=n_samples,
        p=[0.28, 0.14, 0.10, 0.16, 0.17, 0.15],
    )

    country_risk = rng.choice(
        [0, 1],
        size=n_samples,
        p=[0.94, 0.06],
    )

    previous_transaction_count = rng.poisson(
        lam=8,
        size=n_samples,
    )

    account_balance = rng.lognormal(
        mean=8.0,
        sigma=0.9,
        size=n_samples,
    )

    # Fraud probability is generated from several underlying risk signals.
    #
    # These are data-generation relationships, NOT engineered model features.
    # The model receives only the raw columns above.
    fraud_logit = (
        -3.8
        + 1.0 * (transaction_amount > 700)
        + 0.9
        * np.isin(
            transaction_type,
            ["transfer", "cash_withdrawal"],
        )
        + 1.2
        * (
            (transaction_hour <= 4)
            | (transaction_hour >= 23)
        )
        + 1.3 * country_risk
        + 0.8
        * np.isin(
            merchant_category,
            ["electronics", "travel"],
        )
        + 0.7
        * (
            transaction_amount
            > 0.6 * account_balance
        )
    )

    fraud_probability = 1.0 / (
        1.0 + np.exp(-fraud_logit)
    )

    fraud_label = rng.binomial(
        n=1,
        p=fraud_probability,
    )

    return pd.DataFrame(
        {
            "transaction_amount": transaction_amount,
            "transaction_type": transaction_type,
            "account_age_days": account_age_days,
            "transaction_hour": transaction_hour,
            "merchant_category": merchant_category,
            "country_risk": country_risk,
            "previous_transaction_count": (
                previous_transaction_count
            ),
            "account_balance": account_balance,
            TARGET_COLUMN: fraud_label,
        }
    )