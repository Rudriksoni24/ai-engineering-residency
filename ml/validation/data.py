from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ml.data.synthetic import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
)
from ml.validation.contracts import (
    ValidationCheck,
    ValidationResult,
)

ALLOWED_TRANSACTION_TYPES = {
    "card",
    "transfer",
    "cash_withdrawal",
    "bill_payment",
}

ALLOWED_MERCHANT_CATEGORIES = {
    "grocery",
    "electronics",
    "travel",
    "fuel",
    "utilities",
    "other",
}


@dataclass(frozen=True)
class DataValidationPolicy:
    min_rows: int = 500
    max_missing_fraction: float = 0.05
    max_duplicate_fraction: float = 0.01
    min_fraud_rate: float = 0.01
    max_fraud_rate: float = 0.30


class FraudDataValidator:
    def __init__(
        self,
        policy: DataValidationPolicy | None = None,
    ) -> None:
        self.policy = (
            policy
            if policy is not None
            else DataValidationPolicy()
        )

    def validate(
        self,
        dataframe: pd.DataFrame,
    ) -> ValidationResult:
        checks: list[ValidationCheck] = []

        checks.append(
            ValidationCheck(
                name="dataset_not_empty",
                passed=not dataframe.empty,
                message=(
                    "Dataset contains rows"
                    if not dataframe.empty
                    else "Dataset is empty"
                ),
                observed=len(dataframe),
                expected="> 0 rows",
            )
        )

        if dataframe.empty:
            return ValidationResult.from_checks(
                checks
            )

        required = set(
            FEATURE_COLUMNS
            + [TARGET_COLUMN]
        )

        missing_columns = sorted(
            required.difference(
                dataframe.columns
            )
        )

        checks.append(
            ValidationCheck(
                name="required_columns",
                passed=not missing_columns,
                message=(
                    "All required columns exist"
                    if not missing_columns
                    else (
                        "Missing required columns: "
                        f"{missing_columns}"
                    )
                ),
                observed=missing_columns,
                expected=sorted(required),
            )
        )

        if missing_columns:
            return ValidationResult.from_checks(
                checks
            )

        checks.append(
            ValidationCheck(
                name="minimum_dataset_size",
                passed=(
                    len(dataframe)
                    >= self.policy.min_rows
                ),
                message=(
                    "Dataset size is sufficient"
                    if len(dataframe)
                    >= self.policy.min_rows
                    else "Dataset is too small"
                ),
                observed=len(dataframe),
                expected=(
                    f">= {self.policy.min_rows}"
                ),
            )
        )

        self._validate_missingness(
            dataframe,
            checks,
        )

        self._validate_numeric_ranges(
            dataframe,
            checks,
        )

        self._validate_labels(
            dataframe,
            checks,
        )

        self._validate_categories(
            dataframe,
            checks,
        )

        self._validate_duplicates(
            dataframe,
            checks,
        )

        self._validate_class_distribution(
            dataframe,
            checks,
        )

        metrics = {
            "row_count": float(
                len(dataframe)
            ),
            "fraud_rate": float(
                dataframe[TARGET_COLUMN].mean()
            ),
            "duplicate_fraction": float(
                dataframe.duplicated().mean()
            ),
            "maximum_missing_fraction": float(
                dataframe.isna().mean().max()
            ),
        }

        return ValidationResult.from_checks(
            checks,
            metrics=metrics,
        )

    def _validate_missingness(
        self,
        dataframe: pd.DataFrame,
        checks: list[ValidationCheck],
    ) -> None:
        target_missing = int(
            dataframe[
                TARGET_COLUMN
            ].isna().sum()
        )

        checks.append(
            ValidationCheck(
                name="target_not_missing",
                passed=(
                    target_missing == 0
                ),
                message=(
                    "Target contains no missing values"
                    if target_missing == 0
                    else (
                        "Target contains missing "
                        "values"
                    )
                ),
                observed=target_missing,
                expected=0,
            )
        )

        feature_missing_fraction = (
            dataframe[
                FEATURE_COLUMNS
            ].isna().mean().max()
        )

        checks.append(
            ValidationCheck(
                name="feature_missing_fraction",
                passed=(
                    feature_missing_fraction
                    <= self.policy
                    .max_missing_fraction
                ),
                message=(
                    "Feature missingness is within "
                    "policy"
                    if feature_missing_fraction
                    <= self.policy
                    .max_missing_fraction
                    else (
                        "Feature missingness exceeds "
                        "policy"
                    )
                ),
                observed=float(
                    feature_missing_fraction
                ),
                expected=(
                    "<= "
                    f"{self.policy.max_missing_fraction}"
                ),
            )
        )

    def _validate_numeric_ranges(
        self,
        dataframe: pd.DataFrame,
        checks: list[ValidationCheck],
    ) -> None:
        range_rules = {
            "transaction_amount": (
                dataframe[
                    "transaction_amount"
                ].dropna()
                >= 0
            ),
            "account_age_days": (
                dataframe[
                    "account_age_days"
                ].dropna()
                >= 0
            ),
            "transaction_hour": (
                dataframe[
                    "transaction_hour"
                ].dropna()
                .between(
                    0,
                    23,
                    inclusive="both",
                )
            ),
            "country_risk": (
                dataframe[
                    "country_risk"
                ].dropna()
                .isin(
                    [0, 1]
                )
            ),
            "previous_transaction_count": (
                dataframe[
                    "previous_transaction_count"
                ].dropna()
                >= 0
            ),
            "account_balance": (
                dataframe[
                    "account_balance"
                ].dropna()
                >= 0
            ),
        }

        expected = {
            "transaction_amount": ">= 0",
            "account_age_days": ">= 0",
            "transaction_hour": "0..23",
            "country_risk": "{0, 1}",
            "previous_transaction_count": (
                ">= 0"
            ),
            "account_balance": ">= 0",
        }

        for column, valid_mask in (
            range_rules.items()
        ):
            invalid_count = int(
                (~valid_mask).sum()
            )

            checks.append(
                ValidationCheck(
                    name=(
                        f"{column}_range"
                    ),
                    passed=(
                        invalid_count == 0
                    ),
                    message=(
                        f"{column} values are valid"
                        if invalid_count == 0
                        else (
                            f"{column} contains "
                            f"{invalid_count} "
                            "invalid values"
                        )
                    ),
                    observed=invalid_count,
                    expected=expected[column],
                )
            )

    def _validate_labels(
        self,
        dataframe: pd.DataFrame,
        checks: list[ValidationCheck],
    ) -> None:
        labels = set(
            dataframe[
                TARGET_COLUMN
            ].dropna()
            .unique()
            .tolist()
        )

        checks.append(
            ValidationCheck(
                name="label_domain",
                passed=(
                    labels.issubset(
                        {0, 1}
                    )
                ),
                message=(
                    "Target labels are valid"
                    if labels.issubset(
                        {0, 1}
                    )
                    else (
                        "Target contains invalid "
                        "labels"
                    )
                ),
                observed=sorted(labels),
                expected=[0, 1],
            )
        )

        checks.append(
            ValidationCheck(
                name="both_classes_present",
                passed=(
                    labels == {0, 1}
                ),
                message=(
                    "Both target classes are present"
                    if labels == {0, 1}
                    else (
                        "Both target classes must "
                        "be present"
                    )
                ),
                observed=sorted(labels),
                expected=[0, 1],
            )
        )

    def _validate_categories(
        self,
        dataframe: pd.DataFrame,
        checks: list[ValidationCheck],
    ) -> None:
        transaction_types = set(
            dataframe[
                "transaction_type"
            ].dropna()
            .unique()
            .tolist()
        )

        invalid_transaction_types = (
            transaction_types.difference(
                ALLOWED_TRANSACTION_TYPES
            )
        )

        checks.append(
            ValidationCheck(
                name=(
                    "transaction_type_domain"
                ),
                passed=(
                    not invalid_transaction_types
                ),
                message=(
                    "Transaction types are valid"
                    if not invalid_transaction_types
                    else (
                        "Unexpected transaction "
                        "types detected"
                    )
                ),
                observed=sorted(
                    invalid_transaction_types
                ),
                expected=sorted(
                    ALLOWED_TRANSACTION_TYPES
                ),
            )
        )

        categories = set(
            dataframe[
                "merchant_category"
            ].dropna()
            .unique()
            .tolist()
        )

        invalid_categories = (
            categories.difference(
                ALLOWED_MERCHANT_CATEGORIES
            )
        )

        checks.append(
            ValidationCheck(
                name=(
                    "merchant_category_domain"
                ),
                passed=(
                    not invalid_categories
                ),
                message=(
                    "Merchant categories are valid"
                    if not invalid_categories
                    else (
                        "Unexpected merchant "
                        "categories detected"
                    )
                ),
                observed=sorted(
                    invalid_categories
                ),
                expected=sorted(
                    ALLOWED_MERCHANT_CATEGORIES
                ),
            )
        )

    def _validate_duplicates(
        self,
        dataframe: pd.DataFrame,
        checks: list[ValidationCheck],
    ) -> None:
        duplicate_fraction = float(
            dataframe.duplicated().mean()
        )

        checks.append(
            ValidationCheck(
                name="duplicate_fraction",
                passed=(
                    duplicate_fraction
                    <= self.policy
                    .max_duplicate_fraction
                ),
                message=(
                    "Duplicate fraction is within "
                    "policy"
                    if duplicate_fraction
                    <= self.policy
                    .max_duplicate_fraction
                    else (
                        "Duplicate fraction exceeds "
                        "policy"
                    )
                ),
                observed=duplicate_fraction,
                expected=(
                    "<= "
                    f"{self.policy.max_duplicate_fraction}"
                ),
            )
        )

    def _validate_class_distribution(
        self,
        dataframe: pd.DataFrame,
        checks: list[ValidationCheck],
    ) -> None:
        fraud_rate = float(
            dataframe[
                TARGET_COLUMN
            ].mean()
        )

        valid = (
            self.policy.min_fraud_rate
            <= fraud_rate
            <= self.policy.max_fraud_rate
        )

        checks.append(
            ValidationCheck(
                name="fraud_class_distribution",
                passed=valid,
                message=(
                    "Fraud rate is within policy"
                    if valid
                    else (
                        "Fraud rate is outside "
                        "expected policy"
                    )
                ),
                observed=fraud_rate,
                expected=(
                    f"{self.policy.min_fraud_rate}"
                    " <= fraud_rate <= "
                    f"{self.policy.max_fraud_rate}"
                ),
            )
        )