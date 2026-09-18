"""Reusable Sprint 9 transaction data contract."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class TransactionContract(BaseModel):
    """Validated transaction event contract."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    transaction_id: str = Field(min_length=1)
    account_id: str = Field(min_length=1)

    amount: float = Field(gt=0)

    currency: str = Field(
        min_length=3,
        max_length=3,
    )

    merchant_category: str = Field(min_length=1)

    transaction_type: Literal[
        "purchase",
        "withdrawal",
        "transfer",
        "refund",
    ]

    timestamp: datetime

    country: str = Field(
        min_length=2,
        max_length=2,
    )

    device_id: str = Field(min_length=1)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_timezone_aware(
        cls,
        value: datetime,
    ) -> datetime:
        if (
            value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise ValueError(
                "timestamp must be timezone-aware"
            )

        return value

    @field_validator("currency", "country")
    @classmethod
    def normalize_code(
        cls,
        value: str,
    ) -> str:
        return value.upper()