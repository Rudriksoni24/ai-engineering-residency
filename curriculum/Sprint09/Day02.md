# Sprint 9 — Day 2: Kafka Producers and Consumers

## Artifact

Event Pipeline

## Objective

Build a typed Python event pipeline using a Kafka producer and consumer.

## Architecture

```text
Synthetic Transaction
        |
        v
Kafka Producer
        |
        v
transactions topic
        |
        v
Kafka Consumer
        |
        v
Event Handler