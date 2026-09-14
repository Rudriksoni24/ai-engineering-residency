from datetime import datetime, timezone
from typing import Any

import pytest

from streaming.events import TransactionEvent
from streaming.kafka.producer import (
    KafkaTransactionProducer,
)


class FakeProducer:
    def __init__(self) -> None:
        self.messages: list[
            tuple[str, bytes | str | None, bytes | str | None]
        ] = []

        self.poll_calls: list[float] = []
        self.flush_result = 0

    def produce(
        self,
        topic: str,
        *,
        key: bytes | str | None = None,
        value: bytes | str | None = None,
        callback: Any = None,
    ) -> None:
        del callback

        self.messages.append(
            (topic, key, value)
        )

    def poll(self, timeout: float) -> int:
        self.poll_calls.append(timeout)
        return 0

    def flush(
        self,
        timeout: float | None = None,
    ) -> int:
        del timeout
        return self.flush_result


def build_event() -> TransactionEvent:
    return TransactionEvent(
        transaction_id="txn-001",
        account_id="acc-007",
        amount=2500.0,
        currency="INR",
        merchant_category="travel",
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


def test_producer_uses_account_id_as_key() -> None:
    client = FakeProducer()

    producer = KafkaTransactionProducer(
        client,
        topic="transactions",
    )

    event = build_event()

    result = producer.publish(event)

    assert result.transaction_id == "txn-001"
    assert result.topic == "transactions"
    assert result.key == "acc-007"

    assert len(client.messages) == 1

    topic, key, value = client.messages[0]

    assert topic == "transactions"
    assert key == b"acc-007"
    assert value == event.to_json().encode("utf-8")

    assert client.poll_calls == [0]


def test_flush_succeeds_when_queue_is_empty() -> None:
    client = FakeProducer()

    producer = KafkaTransactionProducer(client)

    producer.flush()


def test_flush_raises_when_messages_remain() -> None:
    client = FakeProducer()
    client.flush_result = 2

    producer = KafkaTransactionProducer(client)

    with pytest.raises(
        RuntimeError,
        match="2 Kafka message",
    ):
        producer.flush()