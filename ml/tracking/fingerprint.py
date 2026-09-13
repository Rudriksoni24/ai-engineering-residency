from __future__ import annotations

import hashlib

import pandas as pd


def dataset_fingerprint(
    dataframe: pd.DataFrame,
) -> str:
    """Return a deterministic SHA-256 identity for dataset contents.

    Column names are sorted for canonical serialization while row order is
    deliberately preserved because row ordering can influence deterministic
    splitting behavior.
    """

    if dataframe.empty:
        raise ValueError(
            "Cannot fingerprint an empty dataset"
        )

    canonical = dataframe.loc[
        :,
        sorted(dataframe.columns),
    ]

    serialized = canonical.to_csv(
        index=False,
        lineterminator="\n",
        float_format="%.17g",
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()