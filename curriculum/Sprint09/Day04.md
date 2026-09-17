# Sprint 9 — Day 4: Spark Structured Streaming

## Artifact

Streaming Processing Pipeline

## Objective

Process Kafka transaction events continuously using Spark Structured Streaming
while understanding event time, processing time, checkpoints, triggers,
watermarks, state, and delivery guarantees.

## Architecture

```text
Transaction Producer
        |
        v
Kafka transactions topic
        |
        v
Spark Structured Streaming
        |
        v
Parse JSON
        |
        v
Typed Transaction DataFrame
        |
        v
Validation / Transformation
        |
        v
Streaming Sink


---

#  Architecture and concepts

A Kafka record reaching Spark looks conceptually like:

```text
Kafka
────────────────────────────────────
key       b"acc-001"
value     b'{"transaction_id":...}'
topic     transactions
partition 0
offset    42
timestamp Kafka record timestamp
────────────────────────────────────
              ↓
Spark Kafka source
              ↓
CAST(value AS STRING)
              ↓
from_json(..., TRANSACTION_SCHEMA)
              ↓
transaction_id
account_id
amount
currency
...
timestamp     ← business event time