from datetime import datetime, timezone

import pytest

from streaming.events import (
    TransactionEvent,
    TransactionGenerator,
)


def test_transaction_event_round_trip() -> None:
    event = TransactionEvent(
        transaction_id="txn-001",
        account_id="acc-001",
        amount=1250.50,
        currency="INR",
        merchant_category="electronics",
        transaction_type="purchase",
        timestamp=datetime(
            2026,
            9,
            14,
            8,
            0,
            tzinfo=timezone.utc,
        ),
        country="IN",
        device_id="device-001",
    )

    restored = TransactionEvent.from_json(
        event.to_json()
    )

    assert restored == event


def test_generator_is_deterministic() -> None:
    generator_a = TransactionGenerator(seed=42)
    generator_b = TransactionGenerator(seed=42)

    events_a = list(generator_a.generate(5))
    events_b = list(generator_b.generate(5))

    assert events_a == events_b


def test_generator_creates_unique_transaction_ids() -> None:
    events = list(
        TransactionGenerator(seed=42).generate(10)
    )

    transaction_ids = {
        event.transaction_id
        for event in events
    }

    assert len(transaction_ids) == 10


def test_generator_rejects_negative_count() -> None:
    generator = TransactionGenerator()

    with pytest.raises(
        ValueError,
        match="count must be non-negative",
    ):
        list(generator.generate(-1))


def test_naive_timestamp_is_rejected() -> None:
    payload = """
    {
      "transaction_id": "txn-001",
      "account_id": "acc-001",
      "amount": 100,
      "currency": "INR",
      "merchant_category": "grocery",
      "transaction_type": "purchase",
      "timestamp": "2026-09-14T10:00:00",
      "country": "IN",
      "device_id": "device-001"
    }
    """

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        TransactionEvent.from_json(payload)