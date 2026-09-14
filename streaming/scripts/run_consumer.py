"""Consume synthetic transaction events from Kafka."""

from __future__ import annotations

import argparse
import signal
from types import FrameType

from streaming.kafka.consumer import (
    ConsumedEvent,
    build_kafka_consumer,
)

_running = True


def _stop(
    signum: int,
    frame: FrameType | None,
) -> None:
    del signum, frame

    global _running
    _running = False


def print_event(record: ConsumedEvent) -> None:
    event = record.event

    print(
        "consumed "
        f"transaction_id={event.transaction_id} "
        f"account_id={event.account_id} "
        f"amount={event.amount:.2f} "
        f"currency={event.currency} "
        f"topic={record.topic} "
        f"partition={record.partition} "
        f"offset={record.offset}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consume transaction events from Kafka."
    )

    parser.add_argument(
        "--bootstrap-servers",
        default="localhost:9092",
    )

    parser.add_argument(
        "--group-id",
        default="fraud-event-processor",
    )

    parser.add_argument(
        "--max-messages",
        type=int,
        default=None,
        help="Exit after processing this many messages.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    consumer = build_kafka_consumer(
        bootstrap_servers=args.bootstrap_servers,
        group_id=args.group_id,
    )

    consumed_count = 0

    try:
        while _running:
            processed = consumer.poll_once(
                print_event,
                timeout=1.0,
            )

            if not processed:
                continue

            consumed_count += 1

            if (
                args.max_messages is not None
                and consumed_count >= args.max_messages
            ):
                break

    finally:
        consumer.close()

        print(
            f"consumer stopped "
            f"processed={consumed_count}"
        )


if __name__ == "__main__":
    main()