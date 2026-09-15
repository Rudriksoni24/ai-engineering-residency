"""Small deterministic datasets for local Spark learning."""

from datetime import UTC, datetime

from streaming.events import TransactionEvent


def sample_transactions() -> list[TransactionEvent]:
    """Return deterministic synthetic transaction events."""
    return [
        TransactionEvent(
            transaction_id="txn-001",
            account_id="acc-001",
            amount=1200.0,
            currency="INR",
            merchant_category="grocery",
            transaction_type="purchase",
            timestamp=datetime(
                2026,
                9,
                14,
                8,
                0,
                tzinfo=UTC,
            ),
            country="IN",
            device_id="device-001",
        ),
        TransactionEvent(
            transaction_id="txn-002",
            account_id="acc-001",
            amount=15_000.0,
            currency="INR",
            merchant_category="electronics",
            transaction_type="purchase",
            timestamp=datetime(
                2026,
                9,
                14,
                8,
                5,
                tzinfo=UTC,
            ),
            country="IN",
            device_id="device-001",
        ),
        TransactionEvent(
            transaction_id="txn-003",
            account_id="acc-002",
            amount=850.0,
            currency="INR",
            merchant_category="fuel",
            transaction_type="purchase",
            timestamp=datetime(
                2026,
                9,
                14,
                8,
                10,
                tzinfo=UTC,
            ),
            country="IN",
            device_id="device-002",
        ),
        TransactionEvent(
            transaction_id="txn-004",
            account_id="acc-002",
            amount=24_000.0,
            currency="INR",
            merchant_category="travel",
            transaction_type="purchase",
            timestamp=datetime(
                2026,
                9,
                14,
                8,
                15,
                tzinfo=UTC,
            ),
            country="SG",
            device_id="device-003",
        ),
        TransactionEvent(
            transaction_id="txn-005",
            account_id="acc-003",
            amount=5000.0,
            currency="INR",
            merchant_category="restaurant",
            transaction_type="purchase",
            timestamp=datetime(
                2026,
                9,
                14,
                8,
                20,
                tzinfo=UTC,
            ),
            country="IN",
            device_id="device-004",
        ),
        TransactionEvent(
            transaction_id="txn-006",
            account_id="acc-003",
            amount=32_000.0,
            currency="INR",
            merchant_category="electronics",
            transaction_type="purchase",
            timestamp=datetime(
                2026,
                9,
                14,
                8,
                25,
                tzinfo=UTC,
            ),
            country="US",
            device_id="device-005",
        ),
    ]


def sample_accounts() -> list[tuple[str, str, str]]:
    """Return deterministic account metadata."""
    return [
        (
            "acc-001",
            "premium",
            "IN",
        ),
        (
            "acc-002",
            "standard",
            "IN",
        ),
        (
            "acc-003",
            "premium",
            "IN",
        ),
    ]


def transaction_rows() -> list[tuple[object, ...]]:
    """Convert TransactionEvent instances into Spark row tuples."""
    return [
        (
            event.transaction_id,
            event.account_id,
            event.amount,
            event.currency,
            event.merchant_category,
            event.transaction_type,
            event.timestamp,
            event.country,
            event.device_id,
        )
        for event in sample_transactions()
    ]