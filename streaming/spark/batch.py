"""Spark batch transformations for banking transaction data."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def select_transaction_columns(
    dataframe: DataFrame,
) -> DataFrame:
    """Project the canonical transaction columns."""
    return dataframe.select(
        "transaction_id",
        "account_id",
        "amount",
        "currency",
        "merchant_category",
        "transaction_type",
        "timestamp",
        "country",
        "device_id",
    )


def filter_suspicious_transactions(
    dataframe: DataFrame,
    *,
    amount_threshold: float = 10_000.0,
) -> DataFrame:
    """
    Select high-value transactions.

    This is deliberately a simple learning rule, not a fraud model.
    """
    return dataframe.filter(
        F.col("amount") >= F.lit(amount_threshold)
    )


def aggregate_by_account(
    dataframe: DataFrame,
) -> DataFrame:
    """Calculate transaction statistics per account."""
    return (
        dataframe
        .groupBy("account_id")
        .agg(
            F.count("*").alias("transaction_count"),
            F.round(
                F.sum("amount"),
                2,
            ).alias("total_amount"),
            F.round(
                F.avg("amount"),
                2,
            ).alias("average_amount"),
            F.round(
                F.max("amount"),
                2,
            ).alias("max_amount"),
        )
    )


def aggregate_by_merchant_category(
    dataframe: DataFrame,
) -> DataFrame:
    """Calculate transaction statistics per merchant category."""
    return (
        dataframe
        .groupBy("merchant_category")
        .agg(
            F.count("*").alias("transaction_count"),
            F.round(
                F.sum("amount"),
                2,
            ).alias("total_amount"),
            F.round(
                F.avg("amount"),
                2,
            ).alias("average_amount"),
        )
    )


def calculate_global_statistics(
    dataframe: DataFrame,
) -> DataFrame:
    """Calculate global transaction statistics."""
    return dataframe.agg(
        F.count("*").alias("transaction_count"),
        F.round(
            F.sum("amount"),
            2,
        ).alias("total_amount"),
        F.round(
            F.avg("amount"),
            2,
        ).alias("average_amount"),
        F.round(
            F.min("amount"),
            2,
        ).alias("min_amount"),
        F.round(
            F.max("amount"),
            2,
        ).alias("max_amount"),
    )


def enrich_with_account_metadata(
    transactions: DataFrame,
    accounts: DataFrame,
) -> DataFrame:
    """Join transaction data with account metadata."""
    return transactions.join(
        accounts,
        on="account_id",
        how="left",
    )


def add_country_mismatch_flag(
    dataframe: DataFrame,
) -> DataFrame:
    """
    Identify transactions outside the account's home country.

    Uses Spark-native expressions instead of a Python UDF.
    """
    return dataframe.withColumn(
        "country_mismatch",
        F.col("country") != F.col("home_country"),
    )


def build_processed_transactions(
    transactions: DataFrame,
    accounts: DataFrame,
) -> DataFrame:
    """Build the complete Day 3 enriched transaction dataset."""
    return (
        enrich_with_account_metadata(
            transactions,
            accounts,
        )
        .transform(add_country_mismatch_flag)
        .select(
            "transaction_id",
            "account_id",
            "amount",
            "currency",
            "merchant_category",
            "transaction_type",
            "timestamp",
            "country",
            "device_id",
            "customer_segment",
            "home_country",
            "country_mismatch",
        )
    )