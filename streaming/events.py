"""Synthetic transaction events used throughout Sprint 9."""

from __future__ import annotations

import json
import random
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True, slots=True)
class TransactionEvent:
    """Typed representation of one synthetic banking transaction."""

    transaction_id: str
    account_id: str
    amount: float
    currency: str
    merchant_category: str
    transaction_type: str
    timestamp: datetime
    country: str
    device_id: str

    def to_dict(self) -> dict[str, object]:
        """Convert the event to a JSON-compatible dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    def to_json(self) -> str:
        """Serialize the event deterministically to JSON."""
        return json.dumps(
            self.to_dict(),
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> TransactionEvent:
        """Deserialize JSON into a TransactionEvent."""
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")

        data = json.loads(payload)

        timestamp = datetime.fromisoformat(data["timestamp"])

        if timestamp.tzinfo is None:
            raise ValueError("transaction timestamp must be timezone-aware")

        return cls(
            transaction_id=data["transaction_id"],
            account_id=data["account_id"],
            amount=float(data["amount"]),
            currency=data["currency"],
            merchant_category=data["merchant_category"],
            transaction_type=data["transaction_type"],
            timestamp=timestamp,
            country=data["country"],
            device_id=data["device_id"],
        )


class TransactionGenerator:
    """Generate deterministic synthetic transaction events."""

    _CURRENCIES = ("INR", "USD", "EUR")
    _MERCHANT_CATEGORIES = (
        "grocery",
        "electronics",
        "fuel",
        "restaurant",
        "travel",
        "pharmacy",
    )
    _TRANSACTION_TYPES = (
        "purchase",
        "transfer",
        "withdrawal",
    )
    _COUNTRIES = (
        "IN",
        "US",
        "GB",
        "SG",
    )

    def __init__(
        self,
        *,
        seed: int = 42,
        base_timestamp: datetime | None = None,
    ) -> None:
        self._random = random.Random(seed)

        self._base_timestamp = base_timestamp or datetime(
            2026,
            9,
            14,
            8,
            0,
            tzinfo=UTC,
        )

    def generate(self, count: int) -> Iterator[TransactionEvent]:
        """Generate a deterministic sequence of events."""
        if count < 0:
            raise ValueError("count must be non-negative")

        for index in range(count):
            account_number = self._random.randint(1, 20)
            device_number = self._random.randint(1, 10)

            yield TransactionEvent(
                transaction_id=f"txn-{index + 1:06d}",
                account_id=f"acc-{account_number:04d}",
                amount=round(
                    self._random.uniform(10.0, 50_000.0),
                    2,
                ),
                currency=self._random.choice(self._CURRENCIES),
                merchant_category=self._random.choice(
                    self._MERCHANT_CATEGORIES
                ),
                transaction_type=self._random.choice(
                    self._TRANSACTION_TYPES
                ),
                timestamp=self._base_timestamp
                + timedelta(seconds=index),
                country=self._random.choice(self._COUNTRIES),
                device_id=f"device-{device_number:04d}",
            )