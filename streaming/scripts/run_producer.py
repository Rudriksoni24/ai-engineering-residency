"""Produce deterministic synthetic transactions to Kafka."""

from __future__ import annotations

import argparse

from streaming.events import TransactionGenerator
from streaming.kafka.producer import build_kafka_producer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Produce synthetic transaction events to Kafka."
    )

    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of transaction events to produce.",
    )

    parser.add_argument(
        "--bootstrap-servers",
        default="localhost:9092",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    generator = TransactionGenerator(seed=42)

    producer = build_kafka_producer(
        bootstrap_servers=args.bootstrap_servers,
    )

    try:
        for event in generator.generate(args.count):
            produced = producer.publish(event)

            print(
                "produced "
                f"transaction_id={produced.transaction_id} "
                f"topic={produced.topic} "
                f"key={produced.key}"
            )

        producer.flush()

    finally:
        print("producer finished")


if __name__ == "__main__":
    main()