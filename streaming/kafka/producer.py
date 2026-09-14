"""Kafka transaction producer."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from confluent_kafka import Producer

from streaming.events import TransactionEvent


class ProducerClient(Protocol):
    """Minimal Kafka producer boundary used by application code."""

    def produce(
        self,
        topic: str,
        *,
        key: bytes | str | None = None,
        value: bytes | str | None = None,
        callback: Callable[..., None] | None = None,
    ) -> None:
        ...

    def poll(self, timeout: float) -> int:
        ...

    def flush(self, timeout: float | None = None) -> int:
        ...


@dataclass(frozen=True, slots=True)
class ProducedEvent:
    """Observable metadata returned after enqueueing an event."""

    transaction_id: str
    topic: str
    key: str


class KafkaTransactionProducer:
    """Publish TransactionEvent instances to Kafka."""

    def __init__(
        self,
        client: ProducerClient,
        *,
        topic: str = "transactions",
    ) -> None:
        self._client = client
        self._topic = topic

    def publish(
        self,
        event: TransactionEvent,
    ) -> ProducedEvent:
        """Queue one transaction for delivery."""
        self._client.produce(
            self._topic,
            key=event.account_id.encode("utf-8"),
            value=event.to_json().encode("utf-8"),
            callback=self._delivery_report,
        )

        # Executes queued delivery callbacks without blocking indefinitely.
        self._client.poll(0)

        return ProducedEvent(
            transaction_id=event.transaction_id,
            topic=self._topic,
            key=event.account_id,
        )

    def flush(self, timeout: float = 10.0) -> None:
        """Wait for queued records to be delivered."""
        remaining = self._client.flush(timeout)

        if remaining:
            raise RuntimeError(
                f"{remaining} Kafka message(s) were not delivered "
                f"before flush timeout"
            )

    @staticmethod
    def _delivery_report(error: object, message: object) -> None:
        """Kafka delivery callback."""
        if error is not None:
            raise RuntimeError(
                f"Kafka delivery failed: {error}"
            )


def build_kafka_producer(
    *,
    bootstrap_servers: str = "localhost:9092",
) -> KafkaTransactionProducer:
    """Construct the real Kafka-backed transaction producer."""
    client = Producer(
        {
            "bootstrap.servers": bootstrap_servers,

            # Wait for all in-sync replicas required by the broker.
            "acks": "all",

            # Safe retry behavior.
            "enable.idempotence": True,

            # Bound delivery attempts.
            "delivery.timeout.ms": 30_000,
        }
    )

    return KafkaTransactionProducer(client)