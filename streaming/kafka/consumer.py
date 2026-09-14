"""Kafka transaction consumer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from confluent_kafka import Consumer

from streaming.events import TransactionEvent


class ConsumerMessage(Protocol):
    def error(self) -> object | None:
        ...

    def value(self) -> bytes | None:
        ...

    def key(self) -> bytes | None:
        ...

    def topic(self) -> str:
        ...

    def partition(self) -> int:
        ...

    def offset(self) -> int:
        ...


class ConsumerClient(Protocol):
    """Minimal Kafka consumer boundary."""

    def subscribe(self, topics: list[str]) -> None:
        ...

    def poll(
        self,
        timeout: float,
    ) -> ConsumerMessage | None:
        ...

    def commit(
        self,
        *,
        message: ConsumerMessage,
        asynchronous: bool = False,
    ) -> object:
        ...

    def close(self) -> None:
        ...


@dataclass(frozen=True, slots=True)
class ConsumedEvent:
    """Application-visible record metadata."""

    event: TransactionEvent
    topic: str
    partition: int
    offset: int


EventHandler = Callable[[ConsumedEvent], None]


class KafkaTransactionConsumer:
    """Consume and process TransactionEvent records."""

    def __init__(
        self,
        client: ConsumerClient,
        *,
        topic: str = "transactions",
    ) -> None:
        self._client = client
        self._topic = topic

    def subscribe(self) -> None:
        self._client.subscribe([self._topic])

    def poll_once(
        self,
        handler: EventHandler,
        *,
        timeout: float = 1.0,
    ) -> bool:
        """
        Poll and process one Kafka record.

        Returns True when a record was processed and False when no record
        arrived during the poll interval.
        """
        message = self._client.poll(timeout)

        if message is None:
            return False

        error = message.error()

        if error is not None:
            raise RuntimeError(
                f"Kafka consumer error: {error}"
            )

        value = message.value()

        if value is None:
            raise ValueError(
                "Kafka transaction message has no value"
            )

        event = TransactionEvent.from_json(value)

        consumed = ConsumedEvent(
            event=event,
            topic=message.topic(),
            partition=message.partition(),
            offset=message.offset(),
        )

        # Application processing happens before offset commit.
        handler(consumed)

        # Synchronous commit keeps the learning semantics explicit.
        self._client.commit(
            message=message,
            asynchronous=False,
        )

        return True

    def close(self) -> None:
        self._client.close()


def build_kafka_consumer(
    *,
    bootstrap_servers: str = "localhost:9092",
    group_id: str = "fraud-event-processor",
) -> KafkaTransactionConsumer:
    """Construct the real Kafka-backed transaction consumer."""
    client = Consumer(
        {
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,

            # New groups begin from the start of retained data.
            "auto.offset.reset": "earliest",

            # We explicitly commit only after processing succeeds.
            "enable.auto.commit": False,
        }
    )

    consumer = KafkaTransactionConsumer(client)
    consumer.subscribe()

    return consumer