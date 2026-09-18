from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from streaming.contracts.transaction import (
    TransactionContract,
)


def valid_payload() -> dict:
    return {
        "transaction_id": "txn-001",
        "account_id": "acc-001",
        "amount": 1000.0,
        "currency": "inr",
        "merchant_category": "grocery",
        "transaction_type": "purchase",
        "timestamp": datetime(
            2026,
            9,
            17,
            8,
            0,
            tzinfo=timezone.utc,
        ),
        "country": "in",
        "device_id": "device-001",
    }


def test_valid_transaction() -> None:
    transaction = TransactionContract(
        **valid_payload()
    )

    assert transaction.currency == "INR"
    assert transaction.country == "IN"
    assert transaction.amount == 1000.0


def test_missing_required_field() -> None:
    payload = valid_payload()
    del payload["account_id"]

    with pytest.raises(ValidationError):
        TransactionContract(**payload)


@pytest.mark.parametrize(
    "amount",
    [
        0,
        -1,
        -1000.0,
    ],
)
def test_invalid_amount(
    amount: float,
) -> None:
    payload = valid_payload()
    payload["amount"] = amount

    with pytest.raises(ValidationError):
        TransactionContract(**payload)


def test_invalid_currency() -> None:
    payload = valid_payload()
    payload["currency"] = "RUPEES"

    with pytest.raises(ValidationError):
        TransactionContract(**payload)


def test_invalid_transaction_type() -> None:
    payload = valid_payload()
    payload["transaction_type"] = "unknown"

    with pytest.raises(ValidationError):
        TransactionContract(**payload)


def test_naive_timestamp_rejected() -> None:
    payload = valid_payload()

    payload["timestamp"] = datetime(
        2026,
        9,
        17,
        8,
        0,
    )

    with pytest.raises(
        ValidationError,
        match="timezone-aware",
    ):
        TransactionContract(**payload)


def test_extra_field_rejected() -> None:
    payload = valid_payload()

    payload["unexpected"] = "value"

    with pytest.raises(ValidationError):
        TransactionContract(**payload)