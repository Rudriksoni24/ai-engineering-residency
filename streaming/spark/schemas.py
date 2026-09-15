"""Explicit Spark schemas used by Sprint 9 pipelines."""

from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

TRANSACTION_SCHEMA = StructType(
    [
        StructField(
            "transaction_id",
            StringType(),
            nullable=False,
        ),
        StructField(
            "account_id",
            StringType(),
            nullable=False,
        ),
        StructField(
            "amount",
            DoubleType(),
            nullable=False,
        ),
        StructField(
            "currency",
            StringType(),
            nullable=False,
        ),
        StructField(
            "merchant_category",
            StringType(),
            nullable=False,
        ),
        StructField(
            "transaction_type",
            StringType(),
            nullable=False,
        ),
        StructField(
            "timestamp",
            TimestampType(),
            nullable=False,
        ),
        StructField(
            "country",
            StringType(),
            nullable=False,
        ),
        StructField(
            "device_id",
            StringType(),
            nullable=False,
        ),
    ]
)


ACCOUNT_SCHEMA = StructType(
    [
        StructField(
            "account_id",
            StringType(),
            nullable=False,
        ),
        StructField(
            "customer_segment",
            StringType(),
            nullable=False,
        ),
        StructField(
            "home_country",
            StringType(),
            nullable=False,
        ),
    ]
)