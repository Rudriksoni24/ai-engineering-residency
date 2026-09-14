from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from streaming.events import TransactionEvent
from streaming.kafka.consumer import (
    ConsumedEvent,
    KafkaTransactionConsumer,
)


class FakeMessage:
    def __init__(
        self,
        *,
        value: bytes | None,
        key: bytes | None = b"acc-001",
        error: object | None = None,
        topic: str = "transactions",
        partition: int = 0,
        offset: int = 7,
    ) -> None:
        self._value = value
        self._key = key
        self._error = error
        self._topic = topic
        self._partition = partition
        self._offset = offset

    def value(self) -> bytes | None:
        return self._value

    def key(self) -> bytes | None:
        return self._key

    def error(self) -> object | None:
        return self._error

    def topic(self) -> str:
        return self._topic

    def partition(self) -> int:
        return self._partition

    def offset(self) -> int:
        return self._offset


class FakeConsumer:
    def __init__(
        self,
        messages: list[FakeMessage | None],
    ) -> None:
        self.messages = list(messages)
        self.subscriptions: list[list[str]] = []
        self.commits: list[FakeMessage] = []
        self.closed = False

    def subscribe(
        self,
        topics: list[str],
    ) -> None:
        self.subscriptions.append(topics)

    def poll(
        self,
        timeout: float,
    ) -> FakeMessage | None:
        del timeout

        if not self.messages:
            return None

        return self.messages.pop(0)

    def commit(
        self,
        *,
        message: FakeMessage,
        asynchronous: bool = False,
    ) -> object:
        assert asynchronous is False

        self.commits.append(message)

        return None

    def close(self) -> None:
        self.closed = True


def build_event() -> TransactionEvent:
    return TransactionEvent(
        transaction_id="txn-001",
        account_id="acc-001",
        amount=1000.0,
        currency="INR",
        merchant_category="grocery",
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


def test_consumer_processes_then_commits() -> None:
    event = build_event()

    message = FakeMessage(
        value=event.to_json().encode("utf-8"),
        offset=12,
    )

    client = FakeConsumer([message])

    consumer = KafkaTransactionConsumer(client)

    processed: list[ConsumedEvent] = []

    result = consumer.poll_once(
        processed.append
    )

    assert result is True
    assert len(processed) == 1

    record = processed[0]

    assert record.event == event
    assert record.topic == "transactions"
    assert record.partition == 0
    assert record.offset == 12

    assert client.commits == [message]


def test_consumer_does_not_commit_when_handler_fails() -> None:
    event = build_event()

    message = FakeMessage(
        value=event.to_json().encode("utf-8")
    )

    client = FakeConsumer([message])

    consumer = KafkaTransactionConsumer(client)

    def failing_handler(
        record: ConsumedEvent,
    ) -> None:
        del record
        raise RuntimeError("processing failed")

    with pytest.raises(
        RuntimeError,
        match="processing failed",
    ):
        consumer.poll_once(failing_handler)

    assert client.commits == []


def test_consumer_returns_false_when_no_message() -> None:
    client = FakeConsumer([None])

    consumer = KafkaTransactionConsumer(client)

    processed: list[ConsumedEvent] = []

    assert consumer.poll_once(
        processed.append
    ) is False

    assert processed == []
    assert client.commits == []


def test_consumer_rejects_empty_message() -> None:
    message = FakeMessage(value=None)

    client = FakeConsumer([message])

    consumer = KafkaTransactionConsumer(client)

    with pytest.raises(
        ValueError,
        match="has no value",
    ):
        consumer.poll_once(lambda record: None)

    assert client.commits == []


def test_consumer_closes_client() -> None:
    client = FakeConsumer([])

    consumer = KafkaTransactionConsumer(client)

    consumer.close()

    assert client.closed is True