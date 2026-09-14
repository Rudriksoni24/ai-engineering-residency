# Sprint 9 — Day 2 Report

## Title

Kafka Producers and Consumers

## Artifact

Event Pipeline

## Objective

Build a real Python Kafka producer/consumer pipeline using typed synthetic
banking transaction events.

## Architecture

```text
TransactionGenerator
        |
        v
TransactionEvent
        |
        v
KafkaTransactionProducer
        |
        v
transactions
        |
        v
KafkaTransactionConsumer
        |
        v
Event Handler