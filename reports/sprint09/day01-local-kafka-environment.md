# Sprint 9 — Day 1 Report

## Title

Kafka Fundamentals

## Artifact

Local Kafka Environment

## Objective

Run a local Kafka broker using KRaft mode and validate Kafka's fundamental
operations and architecture.

## Environment

- macOS Apple Silicon
- Colima
- Docker
- Docker Compose
- Apache Kafka 4.3.1
- KRaft
- Single broker/controller node

## Architecture

```text
CLI Producer
     |
     v
transactions
     |
     v
partition 0
     |
     v
Kafka Broker
     |
     v
CLI Consumer